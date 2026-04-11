/*
regex.js

Frontend logic for the Regex -> NFA/DFA page.

Responsibilities:
- Send the regex to the backend to get an NFA and convert to DFA
- Render both NFA and DFA using Cytoscape.js (CDN)
- Animate DFA traversal when the user runs a test string

All functions are documented to explain inputs/outputs and DOM side effects.
*/

// DOM elements
const regexInput = document.getElementById('regex-input');
const testInput = document.getElementById('test-input');
const convertBtn = document.getElementById('convert-btn');
const runBtn = document.getElementById('run-btn');
const resetBtn = document.getElementById('reset-btn');
const stepsList = document.getElementById('steps-list');
const tabButtons = document.querySelectorAll('.tab-btn');
const charDisplay = document.getElementById('char-display');

// Cytoscape instances (kept so we don't re-create on tab switch)
let cyNfa = null;
let cyDfa = null;

// Keep raw data for reuse
let currentNfa = null;
let currentDfa = null;
let currentTestString = '';

// ------------------------- Utility helpers ------------------------- //

/** Clear the step viewer and add a fresh list */
function clearSteps() {
    stepsList.innerHTML = '';
}

/** Append a single step description to the step viewer */
function addStep(text) {
    const li = document.createElement('li');
    li.textContent = text;
    stepsList.appendChild(li);
}

/** Helper to POST JSON and return parsed JSON response */
async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return res.json();
}

/** Build a lookup map from NFA transitions.
 *  This converts the list-of-edges NFA format into a keyed map for faster simulation.
 */
function buildNfaTransitionMap(nfa) {
    const map = {};
    nfa.transitions.forEach(t => {
        if (!map[t.from]) map[t.from] = [];
        map[t.from].push({ symbol: t.symbol, to: t.to });
    });
    return map;
}

/** Compute the epsilon-closure of a set of NFA states.
 *  Returns every state reachable from the current set by following ε-transitions only.
 */
function epsilonClosure(states, transitions) {
    const closure = new Set(states);
    const stack = [...states];
    while (stack.length) {
        const state = stack.pop();
        const edges = transitions[state] || [];
        edges.forEach(({ symbol, to }) => {
            if (symbol === 'ε' && !closure.has(to)) {
                closure.add(to);
                stack.push(to);
            }
        });
    }
    return closure;
}

function nfaMove(states, symbol, transitions) {
    const result = new Set();
    states.forEach(state => {
        const edges = transitions[state] || [];
        edges.forEach(({ symbol: edgeSym, to }) => {
            if (edgeSym === symbol) result.add(to);
        });
    });
    return result;
}

/** Simulate the NFA on the input string and record each reachable state set.
 *  The returned `steps` array includes the initial epsilon-closure before any input
 *  symbol is consumed, and then one entry per consumed symbol.
 */
function runNfaSimulation(nfa, input) {
    const transitions = buildNfaTransitionMap(nfa);
    let current = epsilonClosure(new Set([nfa.start_state]), transitions);
    const steps = [current];
    for (const ch of input) {
        const moved = nfaMove(current, ch, transitions);
        current = epsilonClosure(moved, transitions);
        steps.push(current);
    }
    const valid = current.has(nfa.final_state);
    return { valid, steps };
}

/** Animate the NFA state sets as the input string is consumed.
 *  Highlights all currently active states and the transitions triggered by each symbol.
 */
async function animateNfaPath(steps, input) {
    const delay = 600;
    for (let i = 0; i < steps.length; i++) {
        cyNfa.elements().removeClass('active');
        const activeStates = Array.from(steps[i]);
        activeStates.forEach(state => {
            const node = cyNfa.getElementById('n' + state);
            if (node) node.addClass('active');
        });

        if (i < input.length) {
            const ch = input[i];
            charDisplay.textContent = ch;
            activeStates.forEach(state => {
                const edgeTargets = cyNfa.edges().filter(e =>
                    e.data('source') === 'n' + state &&
                    e.data('label') === ch
                );
                edgeTargets.addClass('active');
            });
        } else {
            charDisplay.textContent = '-';
        }
        await new Promise(r => setTimeout(r, delay));
    }
}

// ------------------------- Cytoscape builders ------------------------- //

/** Build Cytoscape elements for the provided NFA dict.
 *  Node ids are 'n' + stateId to avoid collisions with DFA nodes.
 */
function buildNfaElements(nfa) {
    const nodes = nfa.states.map(s => ({ data: { id: 'n' + s, label: String(s) } }));
    const edges = nfa.transitions.map((t, idx) => ({
        data: {
            id: `ne${idx}`,
            source: 'n' + t.from,
            target: 'n' + t.to,
            label: t.symbol
        }
    }));
    return { nodes, edges };
}

/** Build Cytoscape elements for the DFA.
 *  Node ids are 'd' + stateId. Edge labels are the consumed symbols.
 */
function buildDfaElements(dfa) {
    const nodes = dfa.states.map(s => ({ data: { id: 'd' + s, label: String(s) } }));
    const edges = [];
    // dfa.transitions is an object mapping string stateId -> { symbol: target }
    for (const [state, trans] of Object.entries(dfa.transitions)) {
        const src = 'd' + state;
        for (const [sym, tgt] of Object.entries(trans)) {
            edges.push({ data: { id: `de_${state}_${sym}`, source: src, target: 'd' + tgt, label: sym } });
        }
    }
    return { nodes, edges };
}

/** Create a Cytoscape instance inside `containerId` with given elements.
 *  Returns the cy instance.
 */
function createCy(containerId, elements) {
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
                'height': 40
            }},
            { selector: 'edge', style: {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': '#888',
                'target-arrow-color': '#888',
                'text-rotation': 'autorotate',
                'font-size': 10
            }},
            { selector: '.accept', style: {
                // Attempt to show a double border by increasing border width and using a heavier border
                'border-width': 6,
                'border-style': 'double',
            }},
            { selector: 'node.active', style: {
                'background-color': '#ffe082',
                'border-color': '#ffb300'
            }},
            { selector: 'edge.active', style: {
                'line-color': '#ffb300',
                'target-arrow-color': '#ffb300',
                'width': 4,
                'z-index': 2
            }},
            { selector: '.valid', style: {
                'background-color': '#2e7d32',
                'border-color': '#2e7d32',
                'line-color': '#2e7d32',
                'target-arrow-color': '#2e7d32'
            }},
            { selector: '.invalid', style: {
                'background-color': '#c62828',
                'border-color': '#c62828',
                'line-color': '#c62828',
                'target-arrow-color': '#c62828'
            }}
        ],
        layout: { name: 'cose', animate: true }
    });
}

// ------------------------- Event handlers ------------------------- //

// Tab switching (NFA/DFA). Preserve both cy instances to avoid re-fetching.
tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const target = btn.dataset.target;
        document.querySelectorAll('.diagram').forEach(d => d.classList.remove('active'));
        document.getElementById(target).classList.add('active');
        // Resize Cytoscape to ensure proper rendering when shown
        if (target === 'nfa' && cyNfa) cyNfa.resize();
        if (target === 'dfa' && cyDfa) cyDfa.resize();
    });
});

// Convert button: request NFA and DFA and render both
convertBtn.addEventListener('click', async () => {
    const regex = regexInput.value.trim();
    if (!regex) { alert('Please enter a regular expression.'); return; }

    clearSteps();
    addStep('Tokenizing and compiling regex to NFA...');

    // Request NFA from backend
    const nfaResp = await postJson('/api/regex/nfa', { regex });
    if (nfaResp.error) {
        addStep('Error: ' + nfaResp.error);
        return;
    }
    currentNfa = nfaResp;
    addStep('NFA constructed.');

    // Request DFA conversion
    addStep('Converting NFA to DFA (subset construction)...');
    const dfaResp = await postJson('/api/regex/dfa', { nfa: currentNfa });
    if (dfaResp.error) { addStep('Error: ' + dfaResp.error); return; }
    currentDfa = dfaResp;
    addStep('DFA constructed.');

    // Render NFA and DFA without re-fetching when switching tabs
    const nfaEls = buildNfaElements(currentNfa);
    const dfaEls = buildDfaElements(currentDfa);

    // Destroy existing instances if present
    if (cyNfa) cyNfa.destroy();
    if (cyDfa) cyDfa.destroy();

    cyNfa = createCy('cy-nfa', nfaEls);
    cyDfa = createCy('cy-dfa', dfaEls);

    // Mark accept states in NFA
    const nfaFinal = currentNfa.final_state;
    const nfaFinalNode = cyNfa.getElementById('n' + nfaFinal);
    if (nfaFinalNode) nfaFinalNode.addClass('accept');

    // Mark accept states in DFA
    currentDfa.accept_states.forEach(s => {
        const node = cyDfa.getElementById('d' + s);
        if (node) node.addClass('accept');
    });

    addStep('Diagrams rendered. Switch between NFA and DFA tabs to view.');
});

// Run button: animate DFA traversal using backend path
runBtn.addEventListener('click', async () => {
    const s = testInput.value || '';
    currentTestString = s;
    const activePanel = document.querySelector('.tab-btn.active')?.dataset.target || 'dfa';

    if (activePanel === 'nfa') {
        if (!currentNfa) { alert('Please convert a regex first.'); return; }
        clearSteps();
        addStep('Simulating input on the NFA...');

        const result = runNfaSimulation(currentNfa, s);
        await animateNfaPath(result.steps, s);
        if (result.valid) {
            cyNfa.elements().addClass('valid');
            addStep('Result: VALID (accepted by NFA)');
        } else {
            cyNfa.elements().addClass('invalid');
            addStep('Result: INVALID (rejected by NFA)');
        }
        return;
    }

    if (!currentDfa) { alert('Please convert a regex first.'); return; }
    // Request checker
    const res = await postJson('/api/regex/check', { dfa: currentDfa, string: s });
    if (res.error) { addStep('Error: ' + res.error); return; }

    const path = res.path || [];
    const valid = !!res.valid;

    // Do not force a tab switch; keep the user's current view.
    // The simulation always uses DFA data, but the current tab stays as selected.

    // Animate path: highlight states and edges sequentially
    const delay = 600; // ms
    for (let i = 0; i < path.length; i++) {
        // Clear previous active classes
        cyDfa.elements().removeClass('active');

        const nodeId = 'd' + path[i];
        const node = cyDfa.getElementById(nodeId);
        if (node) node.addClass('active');

        // Show current consumed character (if any)
        if (i < currentTestString.length) {
            const ch = currentTestString[i];
            charDisplay.textContent = ch;
            // Highlight the traversed edge (from path[i] to path[i+1]) if exists
            if (i + 1 < path.length) {
                const nextId = 'd' + path[i + 1];
                const edges = cyDfa.edges().filter(e => e.data('source') === nodeId && e.data('target') === nextId && e.data('label') === ch);
                if (edges && edges.length > 0) edges.addClass('active');
            }
        } else {
            charDisplay.textContent = '-';
        }

        // Wait for delay before next step
        await new Promise(r => setTimeout(r, delay));
    }

    // Final coloring based on validity
    if (valid) {
        cyDfa.elements().addClass('valid');
        addStep('Result: VALID (string accepted by DFA)');
    } else {
        cyDfa.elements().addClass('invalid');
        addStep('Result: INVALID (string rejected by DFA)');
    }
});

// Reset button clears highlights and step viewer
resetBtn.addEventListener('click', () => {
    if (cyNfa) cyNfa.elements().removeClass('active valid invalid');
    if (cyDfa) cyDfa.elements().removeClass('active valid invalid');
    charDisplay.textContent = '-';
    clearSteps();
    addStep('Reset complete.');
});

// Initialize a small starting step
clearSteps();
addStep('Ready. Enter a regex and click Convert.');
