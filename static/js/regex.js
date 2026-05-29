/*
regex.js

Frontend for the Regex -> DFA page.

What it does:
- Loads one of the fixed regex presets, renders its hardcoded minimized DFA in
  Cytoscape, and animates DFA traversals.
- Active edges get a marching-ants effect (animated line-dash-offset) so the
  user can see the direction of travel. The consumed character flashes in the
  shared "Current char" indicator.
*/

// ----------------------------- DOM handles ----------------------------- //
const regexInput = document.getElementById('regex-input');
const testInput  = document.getElementById('test-input');
const runBtn     = document.getElementById('run-btn');
const pauseBtn   = document.getElementById('pause-btn');
const resetBtn   = document.getElementById('reset-btn');
const stepsList  = document.getElementById('steps-list');
const pendingChar = document.getElementById('pending-char');
const verifiedChars = document.getElementById('verified-chars');
const multiStringRows = document.querySelectorAll('#regex-multi-checker .multi-string-row');
const regexChoiceButtons = document.querySelectorAll('.regex-choice');

const fixedRegexes = [
    '(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*',
    '((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*',
];

const hardcodedDfas = [
    {
        states: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        alphabet: ['a', 'b'],
        transitions: {
            '0': { a: 1, b: 2 },
            '1': { a: 3, b: 4 },
            '2': { a: 5, b: 3 },
            '3': { a: 3, b: 3 },
            '4': { a: 6, b: 3 },
            '5': { a: 3, b: 6 },
            '6': { a: 6, b: 7 },
            '7': { a: 8, b: 7 },
            '8': { a: 6, b: 9 },
            '9': { a: 10, b: 10 },
            '10': { a: 10, b: 10 },
        },
        start_state: 0,
        accept_states: [10],
        reject_states: [3],
    },
    {
        states: [0, 1, 2, 3, 4, 5, 6, 7],
        alphabet: ['0', '1'],
        transitions: {
            '0': { 0: 1, 1: 1 },
            '1': { 0: 2, 1: 3 },
            '2': { 0: 4, 1: 3 },
            '3': { 0: 5, 1: 6 },
            '4': { 0: 7, 1: 3 },
            '5': { 0: 4, 1: 7 },
            '6': { 0: 5, 1: 7 },
            '7': { 0: 7, 1: 7 },
        },
        start_state: 0,
        accept_states: [7],
        reject_states: [],
    },
];

const dfaPositions = [
    {
        0: { x: 80, y: 210 },
        1: { x: 210, y: 110 },
        2: { x: 210, y: 310 },
        3: { x: 340, y: 210 },
        4: { x: 470, y: 110 },
        5: { x: 470, y: 310 },
        6: { x: 600, y: 210 },
        7: { x: 730, y: 90 },
        8: { x: 860, y: 210 },
        9: { x: 990, y: 210 },
        10: { x: 1120, y: 210 },
    },
    {
        0: { x: 90, y: 210 },
        1: { x: 230, y: 210 },
        2: { x: 370, y: 110 },
        3: { x: 370, y: 310 },
        4: { x: 510, y: 110 },
        5: { x: 510, y: 310 },
        6: { x: 650, y: 210 },
        7: { x: 790, y: 210 },
    },
];

// Persistent Cytoscape instance and the selected hardcoded automaton.
let cyDfa = null;
let currentDfa = null;
let currentTestString = '';
let selectedRegexIndex = 0;
let dfaRunToken = 0;
let dfaPaused = false;
let dfaPauseWaiters = [];

// ----------------------------- Utilities ----------------------------- //

function clearSteps() { stepsList.innerHTML = ''; }
function addStep(text) {
    const li = document.createElement('li');
    li.textContent = text;
    stepsList.appendChild(li);
    // Keep the newest step visible inside the scrollable step viewer.
    stepsList.scrollTop = stepsList.scrollHeight;
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function releaseDfaPauseWaiters() {
    const waiters = dfaPauseWaiters.splice(0);
    waiters.forEach(resolve => resolve());
}

function setDfaPaused(paused) {
    dfaPaused = paused;
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    if (!paused) releaseDfaPauseWaiters();
}

function setDfaPauseEnabled(enabled) {
    pauseBtn.disabled = !enabled;
    if (!enabled) setDfaPaused(false);
}

async function waitWhileDfaPaused(token) {
    while (dfaPaused && token === dfaRunToken) {
        await new Promise(resolve => dfaPauseWaiters.push(resolve));
    }
    return token === dfaRunToken;
}

function cancelDfaRun() {
    dfaRunToken++;
    setDfaPauseEnabled(false);
    stopAnts();
}

function scrollDfaVisualizerIntoView() {
    document.getElementById('diagram-panel')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
    });
}

function showFixedRegex(index) {
    cancelDfaRun();
    selectedRegexIndex = index;
    regexInput.value = fixedRegexes[index];
    regexChoiceButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.regex === String(index));
    });
    resetCharTape();
    clearSteps();
    loadSelectedDfa();
}

regexChoiceButtons.forEach(btn => {
    btn.addEventListener('click', () => showFixedRegex(Number(btn.dataset.regex)));
});

function setPendingChar(ch, state = 'pending') {
    pendingChar.textContent = (ch === null || ch === undefined || ch === '') ? '-' : ch;
    pendingChar.className = `char-token ${state}${pendingChar.textContent === '-' ? ' empty' : ''}`;
}

function resetCharTape() {
    verifiedChars.innerHTML = '';
    setPendingChar(null, 'empty');
}

function addVerifiedChar(ch) {
    if (ch === null || ch === undefined || ch === '') return;
    const token = document.createElement('span');
    token.className = 'char-token accepted';
    token.textContent = ch;
    verifiedChars.appendChild(token);
}

function showRejectedChar(ch) {
    setPendingChar(ch, 'rejected');
}

function prepareCharTape(input) {
    verifiedChars.innerHTML = '';
    setPendingChar(input.length ? input[0] : null, input.length ? 'pending' : 'empty');
}

function advanceCharTape(input, index) {
    addVerifiedChar(input[index]);
    const next = input[index + 1];
    setPendingChar(next, next === undefined ? 'empty' : 'pending');
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
    if (!currentDfa) return { valid: false, path: [] };

    const acceptStates = new Set(currentDfa.accept_states);
    const rejectStates = new Set(currentDfa.reject_states || []);
    const path = [currentDfa.start_state];
    let current = currentDfa.start_state;
    let rejectedAt = null;
    let rejectedChar = null;

    for (let i = 0; i < value.length; i++) {
        const ch = value[i];
        const next = currentDfa.transitions[String(current)] &&
            currentDfa.transitions[String(current)][ch];
        if (next === undefined) {
            return { valid: false, path, rejectedAt: i, rejectedChar: ch };
        }
        current = next;
        path.push(current);
        if (rejectStates.has(current) && rejectedAt === null) {
            rejectedAt = i;
            rejectedChar = ch;
            break;
        }
    }

    return {
        valid: acceptStates.has(current) && rejectedAt === null,
        path,
        rejectedAt,
        rejectedChar,
    };
}

async function checkStringRow(row) {
    if (!currentDfa) return;
    const input = row.querySelector('.multi-string-input');
    const value = input.value || '';
    const res = await checkRegexString(value);
    setStringResult(row, !!res.valid, value, res.error);
}

async function checkAllRegexStrings() {
    if (!currentDfa) return;
    await Promise.all(Array.from(multiStringRows).map(checkStringRow));
}

function loadSelectedDfa() {
    currentDfa = hardcodedDfas[selectedRegexIndex];

    const dfaEls = buildDfaElements(currentDfa);
    if (cyDfa) cyDfa.destroy();
    cyDfa = createCy('cy-dfa', dfaEls);

    currentDfa.accept_states.forEach(s => {
        const node = cyDfa.getElementById('d' + s);
        if (node) node.addClass('accept');
    });
    resetViewport(cyDfa);

    resetStringResults();
    checkAllRegexStrings();
    addStep('DFA visualization ready.');
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
        const cy = cyDfa;
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

function buildDfaElements(dfa) {
    const positions = dfaPositions[selectedRegexIndex];
    const nodes = dfa.states.map(s => ({
        data: { id: 'd' + s, label: String(s) },
        position: positions[s],
    }));
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
 *  this keeps state-machine diagrams compact and matches how automata are
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
    return cytoscape({
        container: document.getElementById(containerId),
        elements: elements.nodes.concat(elements.edges),
        style: [
            { selector: 'node', style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#fff',
                'border-color': '#25364d',
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
                'line-color': '#8a97a8',
                'target-arrow-color': '#8a97a8',
                'text-rotation': 'autorotate',
                'font-size': 10,
                'transition-property': 'line-color, target-arrow-color, width',
                'transition-duration': 150,
            }},
            { selector: '.accept', style: {
                'border-width': 3,
                'border-style': 'solid',
            }},
            { selector: '.active', style: {
                'background-color': '#e4f5f2',
                'border-color': '#0f766e',
                'border-width': 4,
            }},
            { selector: '.pulse', style: {
                'width': 52,
                'height': 52,
                'border-color': '#0f766e',
                'border-width': 6,
            }},
            { selector: 'edge.traversing', style: {
                'line-color': '#0f766e',
                'target-arrow-color': '#0f766e',
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
        minZoom: 0.45,
        maxZoom: 2.4,
        wheelSensitivity: 0.18,
        layout: { name: 'preset', fit: true, padding: 35 },
    });
}

function resetViewport(cy) {
    if (!cy || cy.destroyed()) return;
    cy.fit(cy.elements(), 35);
}

function keepElementInView(cy, ele) {
    if (!cy || !ele || ele.empty()) return;
    const container = cy.container();
    const width = container.clientWidth;
    const height = container.clientHeight;
    const rbb = ele.renderedBoundingBox({ includeLabels: false });
    const margin = 70;
    const outOfView = (
        rbb.x1 < margin ||
        rbb.x2 > width - margin ||
        rbb.y1 < margin ||
        rbb.y2 > height - margin
    );

    if (!outOfView) return;
    cy.animate({ center: { eles: ele }, duration: 260, easing: 'ease-in-out' });
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

multiStringRows.forEach(row => {
    const input = row.querySelector('.multi-string-input');
    const simulateBtn = row.querySelector('.simulate-string-btn');
    input.addEventListener('input', () => checkStringRow(row));
    simulateBtn.addEventListener('click', async () => {
        if (!currentDfa) loadSelectedDfa();
        testInput.value = input.value || '';
        currentTestString = testInput.value;
        await checkStringRow(row);
        scrollDfaVisualizerIntoView();
        await runDfa(currentTestString);
    });
});

// ----------------------------- Run ----------------------------- //

pauseBtn.addEventListener('click', () => {
    if (pauseBtn.disabled) return;
    setDfaPaused(!dfaPaused);
});

runBtn.addEventListener('click', async () => {
    if (!currentDfa) loadSelectedDfa();
    const s = testInput.value || '';
    currentTestString = s;
    await runDfa(s);
});

async function runDfa(s) {
    const token = ++dfaRunToken;
    setDfaPaused(false);
    setDfaPauseEnabled(true);
    const res = await checkRegexString(s);
    if (res.error) {
        addStep('Error: ' + res.error);
        setDfaPauseEnabled(false);
        return;
    }
    const path = res.path || [];
    const valid = !!res.valid;
    const rejectedAt = res.rejectedAt;

    cyDfa.elements().removeClass('active traversing valid invalid pulse');
    prepareCharTape(currentTestString);
    startAnts();

    const delay = 700;
    try {
        for (let i = 0; i < path.length; i++) {
            if (!(await waitWhileDfaPaused(token))) return;

            // Reset transient highlights from the previous frame.
            cyDfa.nodes('.active').removeClass('active');
            cyDfa.edges('.traversing').removeClass('traversing');

            const nodeId = 'd' + path[i];
            const node = cyDfa.getElementById(nodeId);
            if (node) {
                node.addClass('active');
                pulseNode(node);
                keepElementInView(cyDfa, node);
            }

            // Flash the just-consumed character and light up the edge for it.
            if (i < currentTestString.length) {
                const ch = currentTestString[i];
                if (i + 1 < path.length) {
                    const nextId = 'd' + path[i + 1];
                    findEdge(cyDfa, nodeId, nextId, ch).addClass('traversing');
                }
                if (rejectedAt === i) {
                    showRejectedChar(ch);
                } else {
                    advanceCharTape(currentTestString, i);
                }
            } else {
                setPendingChar(null, 'empty');
            }

            await sleep(delay);
            if (token !== dfaRunToken) return;
            if (rejectedAt === i) break;
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
    } finally {
        if (token === dfaRunToken) setDfaPauseEnabled(false);
    }
}

// ----------------------------- Reset ----------------------------- //

resetBtn.addEventListener('click', async () => {
    cancelDfaRun();
    if (cyDfa) cyDfa.elements().removeClass('active traversing valid invalid pulse');
    resetViewport(cyDfa);
    resetCharTape();
    resetStringResults();
    await checkAllRegexStrings();
    clearSteps();
    addStep('Reset complete. DFA visualization is ready.');
});

// ----------------------------- Init ----------------------------- //
clearSteps();
showFixedRegex(selectedRegexIndex);
