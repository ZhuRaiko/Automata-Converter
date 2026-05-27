/*
regex.js

Frontend for the Regex -> NFA/DFA page.

What it does:
- Sends the regex to the backend, builds the NFA + minimized DFA, renders both
  in Cytoscape, and animates traversals.
- The "Run" button now respects whichever tab is currently active: NFA tab
  -> backend NFA simulator + active-set animation; DFA tab -> backend DFA
  checker + single-path animation.
- Active edges get a marching-ants effect (animated line-dash-offset) so the
  user can see the direction of travel. The consumed character flashes in the
  shared "Current char" indicator.
*/

// ----------------------------- DOM handles ----------------------------- //
const regexInput = document.getElementById('regex-input');
const testInput  = document.getElementById('test-input');
const convertBtn = document.getElementById('convert-btn');
const runBtn     = document.getElementById('run-btn');
const resetBtn   = document.getElementById('reset-btn');
const stepsList  = document.getElementById('steps-list');
const tabButtons = document.querySelectorAll('.tab-btn');
const charDisplay = document.getElementById('char-display');
const multiStringRows = document.querySelectorAll('#regex-multi-checker .multi-string-row');

// Persistent Cytoscape instances and the last computed automata.
let cyNfa = null;
let cyDfa = null;
let currentNfa = null;
let currentDfa = null;
let currentTestString = '';

// ----------------------------- Utilities ----------------------------- //

function clearSteps() { stepsList.innerHTML = ''; }
function addStep(text) {
    const li = document.createElement('li');
    li.textContent = text;
    stepsList.appendChild(li);
    // Keep the newest step visible inside the scrollable step viewer.
    stepsList.scrollTop = stepsList.scrollHeight;
}
async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return res.json();
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/** Flash the current-character indicator. Removing+re-adding the class with
 *  a forced reflow restarts the keyframe animation each time. */
function flashChar(ch) {
    charDisplay.textContent = (ch === null || ch === undefined || ch === '') ? '-' : ch;
    charDisplay.classList.remove('flash');
    // Force reflow so the animation re-triggers next paint.
    void charDisplay.offsetWidth;
    charDisplay.classList.add('flash');
}

/** Which automaton diagram is the user currently looking at? */
function activeTabTarget() {
    const btn = document.querySelector('.tab-btn.active');
    return btn ? btn.dataset.target : 'nfa';
}

function setStringResult(row, valid, value, error) {
    const result = row.querySelector('.string-result');
    result.classList.remove('pending', 'accepted', 'rejected');
    if (error) {
        result.classList.add('rejected');
        result.textContent = 'Error';
        return;
    }
    result.classList.add(valid ? 'accepted' : 'rejected');
    if (value === '') {
        result.textContent = valid ? 'Null String Accepted' : 'Null String Not Accepted';
    } else {
        result.textContent = valid ? 'String Accepted' : 'String Not Accepted';
    }
}

function resetStringResults() {
    multiStringRows.forEach(row => {
        const result = row.querySelector('.string-result');
        result.classList.remove('accepted', 'rejected');
        result.classList.add('pending');
        result.textContent = 'Not Checked';
    });
}

async function checkRegexString(value) {
    if (activeTabTarget() === 'nfa') {
        return postJson('/api/regex/nfa/check', { nfa: currentNfa, string: value });
    }
    return postJson('/api/regex/check', { dfa: currentDfa, string: value });
}

async function checkStringRow(row) {
    if (!currentNfa || (activeTabTarget() === 'dfa' && !currentDfa)) return;
    const input = row.querySelector('.multi-string-input');
    const value = input.value || '';
    const res = await checkRegexString(value);
    setStringResult(row, !!res.valid, value, res.error);
}

async function checkAllRegexStrings() {
    if (!currentNfa || (activeTabTarget() === 'dfa' && !currentDfa)) return;
    await Promise.all(Array.from(multiStringRows).map(checkStringRow));
}

// ----------------------------- Marching-ants animation ----------------------------- //
// One global animator drives all active edges on the visible Cytoscape so the
// dash offset progresses smoothly. The handle is restarted between runs.

let antsTimer = null;
let antsOffset = 0;
function startAnts() {
    if (antsTimer) return;
    antsTimer = setInterval(() => {
        antsOffset = (antsOffset - 3) % 1000;
        const cy = activeTabTarget() === 'nfa' ? cyNfa : cyDfa;
        if (!cy) return;
        cy.edges('.traversing').forEach(e => {
            e.style('line-dash-offset', antsOffset);
        });
    }, 60);
}
function stopAnts() {
    if (antsTimer) { clearInterval(antsTimer); antsTimer = null; }
}

// ----------------------------- Cytoscape builders ----------------------------- //

function buildNfaElements(nfa) {
    const nodes = nfa.states.map(s => ({ data: { id: 'n' + s, label: String(s) } }));
    const edges = nfa.transitions.map((t, idx) => ({
        data: {
            id: `ne${idx}`,
            source: 'n' + t.from,
            target: 'n' + t.to,
            label: t.symbol,
            symbol: t.symbol,
        },
    }));
    return { nodes, edges };
}

function buildDfaElements(dfa) {
    const nodes = dfa.states.map(s => ({ data: { id: 'd' + s, label: String(s) } }));
    const edges = [];
    for (const [state, trans] of Object.entries(dfa.transitions)) {
        const src = 'd' + state;
        for (const [sym, tgt] of Object.entries(trans)) {
            edges.push({
                data: {
                    id: `de_${state}_${sym}`,
                    source: src,
                    target: 'd' + tgt,
                    label: sym,
                    symbol: sym,
                },
            });
        }
    }
    return { nodes, edges };
}

/** Shared Cytoscape factory. Uses the dagre layered layout (loaded via the
 *  cytoscape-dagre CDN) with rankDir 'LR' so states flow left-to-right —
 *  this keeps NFA diagrams compact and matches how state machines are
 *  typically drawn in textbooks.
 *
 *  Additional style selectors over the default Cytoscape setup:
 *    - `.traversing` on an edge -> bright orange dashed line; the marching-ants
 *      timer animates `line-dash-offset` on these so the dashes "flow" toward
 *      the target.
 *    - `.pulse` on a node -> larger highlight ring (set transiently when a
 *      state becomes active).
 */
function createCy(containerId, elements) {
    // Prefer dagre when available (loaded from the CDN above); fall back to
    // cose so the page still works offline / if the extension fails to load.
    const layout = (typeof cytoscape.use === 'function' && window.dagre !== false)
        ? { name: 'dagre', rankDir: 'LR', nodeSep: 30, rankSep: 60, animate: false }
        : { name: 'cose', animate: true };
    return cytoscape({
        container: document.getElementById(containerId),
        elements: elements.nodes.concat(elements.edges),
        style: [
            { selector: 'node', style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#fff',
                'border-color': '#333',
                'border-width': 2,
                'width': 40,
                'height': 40,
                'transition-property': 'background-color, border-color, border-width, width, height',
                'transition-duration': 180,
            }},
            { selector: 'edge', style: {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': '#888',
                'target-arrow-color': '#888',
                'text-rotation': 'autorotate',
                'font-size': 10,
                'transition-property': 'line-color, target-arrow-color, width',
                'transition-duration': 150,
            }},
            { selector: '.accept', style: {
                'border-width': 6,
                'border-style': 'double',
            }},
            { selector: '.active', style: {
                'background-color': '#ffe082',
                'border-color': '#ffb300',
                'border-width': 4,
            }},
            { selector: '.pulse', style: {
                'width': 52,
                'height': 52,
                'border-color': '#ff9800',
                'border-width': 6,
            }},
            { selector: 'edge.traversing', style: {
                'line-color': '#ff9800',
                'target-arrow-color': '#ff9800',
                'line-style': 'dashed',
                'line-dash-pattern': [8, 4],
                'width': 4,
            }},
            { selector: '.valid', style: {
                'background-color': '#2e7d32',
                'border-color': '#2e7d32',
                'line-color': '#2e7d32',
                'target-arrow-color': '#2e7d32',
            }},
            { selector: '.invalid', style: {
                'background-color': '#c62828',
                'border-color': '#c62828',
                'line-color': '#c62828',
                'target-arrow-color': '#c62828',
            }},
        ],
        layout: layout,
    });
}

// ----------------------------- Animation helpers ----------------------------- //

/** Briefly grow + glow a node (independent of its sticky `.active` class). */
function pulseNode(node) {
    if (!node) return;
    node.addClass('pulse');
    setTimeout(() => node.removeClass('pulse'), 280);
}

/** Find an edge in `cy` by (source, target, symbol). */
function findEdge(cy, srcId, tgtId, sym) {
    return cy.edges().filter(e =>
        e.data('source') === srcId &&
        e.data('target') === tgtId &&
        (sym === undefined || e.data('symbol') === sym)
    );
}

// ----------------------------- Tab switching ----------------------------- //

tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const target = btn.dataset.target;
        document.querySelectorAll('.diagram').forEach(d => d.classList.remove('active'));
        document.getElementById(target).classList.add('active');
        // Cytoscape needs a resize() after the container becomes visible.
        if (target === 'nfa' && cyNfa) cyNfa.resize();
        if (target === 'dfa' && cyDfa) cyDfa.resize();
        checkAllRegexStrings();
    });
});

multiStringRows.forEach(row => {
    const input = row.querySelector('.multi-string-input');
    const simulateBtn = row.querySelector('.simulate-string-btn');
    input.addEventListener('input', () => checkStringRow(row));
    simulateBtn.addEventListener('click', async () => {
        if (!currentNfa) { alert('Please convert a regex first.'); return; }
        testInput.value = input.value || '';
        currentTestString = testInput.value;
        await checkStringRow(row);
        if (activeTabTarget() === 'nfa') {
            await runNfa(currentTestString);
        } else {
            await runDfa(currentTestString);
        }
    });
});

// ----------------------------- Convert ----------------------------- //

convertBtn.addEventListener('click', async () => {
    const regex = regexInput.value.trim();
    if (!regex) { alert('Please enter a regular expression.'); return; }

    clearSteps();
    addStep('Tokenizing and compiling regex to NFA...');

    const nfaResp = await postJson('/api/regex/nfa', { regex });
    if (nfaResp.error) { addStep('Error: ' + nfaResp.error); return; }
    currentNfa = nfaResp;
    addStep('NFA constructed.');

    addStep('Converting NFA to DFA (subset construction + minimization)...');
    const dfaResp = await postJson('/api/regex/dfa', { nfa: currentNfa });
    if (dfaResp.error) { addStep('Error: ' + dfaResp.error); return; }
    currentDfa = dfaResp;
    addStep('Minimal DFA constructed.');

    const nfaEls = buildNfaElements(currentNfa);
    const dfaEls = buildDfaElements(currentDfa);

    if (cyNfa) cyNfa.destroy();
    if (cyDfa) cyDfa.destroy();
    cyNfa = createCy('cy-nfa', nfaEls);
    cyDfa = createCy('cy-dfa', dfaEls);

    // Mark accept states.
    const nfaFinalNode = cyNfa.getElementById('n' + currentNfa.final_state);
    if (nfaFinalNode) nfaFinalNode.addClass('accept');
    currentDfa.accept_states.forEach(s => {
        const node = cyDfa.getElementById('d' + s);
        if (node) node.addClass('accept');
    });

    await checkAllRegexStrings();
    addStep('Diagrams rendered. Switch tabs to compare NFA and DFA.');
});

// ----------------------------- Run (tab-aware) ----------------------------- //

runBtn.addEventListener('click', async () => {
    if (!currentNfa) { alert('Please convert a regex first.'); return; }
    const s = testInput.value || '';
    currentTestString = s;

    if (activeTabTarget() === 'nfa') {
        await runNfa(s);
    } else {
        await runDfa(s);
    }
});

/** NFA animation. The backend returns a single accepting path
 *  (JFLAP "fast run" style): one state active per step, one edge fires per
 *  step. Epsilon moves are their own steps with char = 'ε'. */
async function runNfa(s) {
    const res = await postJson('/api/regex/nfa/check', { nfa: currentNfa, string: s });
    if (res.error) { addStep('Error: ' + res.error); return; }
    const steps = res.steps || [];
    const valid = !!res.valid;

    cyNfa.elements().removeClass('active traversing valid invalid pulse');
    startAnts();

    const delay = 700;
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];

        cyNfa.nodes('.active').removeClass('active');
        cyNfa.edges('.traversing').removeClass('traversing');

        const node = cyNfa.getElementById('n' + step.state);
        if (node) {
            node.addClass('active');
            pulseNode(node);
        }

        if (step.edge) {
            findEdge(cyNfa,
                'n' + step.edge.from,
                'n' + step.edge.to,
                step.edge.symbol
            ).addClass('traversing');
        }

        if (step.char !== null && step.char !== undefined) {
            flashChar(step.char);
        } else {
            charDisplay.textContent = '-';
        }

        const edgeStr = step.edge ? ` via ${step.edge.from} --${step.edge.symbol}--> ${step.edge.to}` : ' (start)';
        addStep(`Step ${i}: state=${step.state} remaining="${step.remaining_input}"${edgeStr}`);
        await sleep(delay);
    }

    cyNfa.edges('.traversing').removeClass('traversing');
    stopAnts();

    if (valid) {
        cyNfa.elements().addClass('valid');
        addStep('Result: VALID (string accepted by NFA)');
    } else {
        cyNfa.elements().addClass('invalid');
        addStep('Result: INVALID (string rejected by NFA — trace shows farthest progress)');
    }
}

async function runDfa(s) {
    const res = await postJson('/api/regex/check', { dfa: currentDfa, string: s });
    if (res.error) { addStep('Error: ' + res.error); return; }
    const path = res.path || [];
    const valid = !!res.valid;

    cyDfa.elements().removeClass('active traversing valid invalid pulse');
    startAnts();

    const delay = 700;
    for (let i = 0; i < path.length; i++) {
        // Reset transient highlights from the previous frame.
        cyDfa.nodes('.active').removeClass('active');
        cyDfa.edges('.traversing').removeClass('traversing');

        const nodeId = 'd' + path[i];
        const node = cyDfa.getElementById(nodeId);
        if (node) {
            node.addClass('active');
            pulseNode(node);
        }

        // Flash the just-consumed character and light up the edge for it.
        if (i < currentTestString.length) {
            const ch = currentTestString[i];
            flashChar(ch);
            if (i + 1 < path.length) {
                const nextId = 'd' + path[i + 1];
                findEdge(cyDfa, nodeId, nextId, ch).addClass('traversing');
            }
        } else {
            charDisplay.textContent = '-';
        }

        await sleep(delay);
    }

    cyDfa.edges('.traversing').removeClass('traversing');
    stopAnts();

    if (valid) {
        cyDfa.elements().addClass('valid');
        addStep('Result: VALID (string accepted by DFA)');
    } else {
        cyDfa.elements().addClass('invalid');
        addStep('Result: INVALID (string rejected by DFA)');
    }
}

// ----------------------------- Reset ----------------------------- //

resetBtn.addEventListener('click', () => {
    stopAnts();
    if (cyNfa) cyNfa.elements().removeClass('active traversing valid invalid pulse');
    if (cyDfa) cyDfa.elements().removeClass('active traversing valid invalid pulse');
    charDisplay.textContent = '-';
    charDisplay.classList.remove('flash');
    resetStringResults();
    clearSteps();
    addStep('Reset complete.');
});

// ----------------------------- Init ----------------------------- //
clearSteps();
addStep('Ready. Enter a regex and click Convert.');
