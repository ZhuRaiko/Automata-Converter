/*
cfg.js

Frontend for the CFG -> PDA page.

What it does:
- Shows one of the fixed converted CFGs, then renders a hardcoded PDA
  flowchart driven by the same single-character transition flow as the DFA.
- Checks test strings against the hardcoded DFA flow and animates a compact
  PDA-style READ flowchart:
    * the active state lights up (sticky) and pulses on entry,
    * the transition edge between consecutive states gets "marching ants"
      (animated line-dash-offset) so the direction of travel is obvious,
    * the input tape shows which character is being verified.
*/

const cfgInput = document.getElementById('cfg-input');
const cfgRunBtn = document.getElementById('cfg-run-btn');
const cfgPauseBtn = document.getElementById('cfg-pause-btn');
const cfgResetBtn = document.getElementById('cfg-reset-btn');
const cfgStepsList = document.getElementById('cfg-steps-list');
const cfgPendingChar = document.getElementById('cfg-pending-char');
const cfgVerifiedChars = document.getElementById('cfg-verified-chars');
const cfgMultiStringRows = document.querySelectorAll('#cfg-multi-checker .multi-string-row');
const cfgChoiceButtons = document.querySelectorAll('.cfg-choice');
const ACCEPT_MARKER = '\u0394';

const convertedCfgs = [
    `S -> P A bab A Q R
P -> aba | bab
A -> aA | bA | ε
Q -> a | b | ab | ba
R -> aR | bR | aaR | ε`,
    `S -> X Y Z W
X -> 101 | 111 | 1 | 0 | 11
Y -> 1Y | 0Y | 01Y | ε
Z -> 111 | 000 | 101
W -> 1W | 0W | ε`,
];

let cyPda = null;
let currentPda = null;
let currentSteps = null;
let selectedCfgIndex = 0;
let pdaRunToken = 0;
let pdaPaused = false;
let pdaPauseWaiters = [];

function releasePdaPauseWaiters() {
    const waiters = pdaPauseWaiters.splice(0);
    waiters.forEach(resolve => resolve());
}

function setPdaPaused(paused) {
    pdaPaused = paused;
    cfgPauseBtn.textContent = paused ? 'Resume' : 'Pause';
    if (!paused) releasePdaPauseWaiters();
}

function setPdaPauseEnabled(enabled) {
    cfgPauseBtn.disabled = !enabled;
    if (!enabled) setPdaPaused(false);
}

async function waitWhilePdaPaused(token) {
    while (pdaPaused && token === pdaRunToken) {
        await new Promise(resolve => pdaPauseWaiters.push(resolve));
    }
    return token === pdaRunToken;
}

function cancelPdaRun() {
    pdaRunToken++;
    setPdaPauseEnabled(false);
    stopAnts();
}

function scrollPdaVisualizerIntoView() {
    document.getElementById('cfg-diagram-section')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
    });
}

function resetCurrentCfg() {
    cancelPdaRun();
    currentPda = null;
    currentSteps = null;
    if (cyPda) {
        cyPda.destroy();
        cyPda = null;
    }
    resetCfgStringResults();
    clearCfgSteps();
    addCfgStep('Ready. Choose a CFG.');
}

function showConvertedCfg(index) {
    cancelPdaRun();
    selectedCfgIndex = index;
    cfgInput.value = convertedCfgs[index];
    cfgChoiceButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.cfg === String(index));
    });
    loadSelectedCfgFlow();
}

cfgChoiceButtons.forEach(btn => {
    btn.addEventListener('click', () => showConvertedCfg(Number(btn.dataset.cfg)));
});

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function clearCfgSteps() { cfgStepsList.innerHTML = ''; }

function addCfgStep(text) {
    const li = document.createElement('li');
    li.textContent = text;
    cfgStepsList.appendChild(li);
    cfgStepsList.scrollTop = cfgStepsList.scrollHeight;
}

function setCfgPendingChar(ch, state = 'pending') {
    cfgPendingChar.textContent = (ch === null || ch === undefined || ch === '') ? '-' : ch;
    cfgPendingChar.className = `char-token ${state}${cfgPendingChar.textContent === '-' ? ' empty' : ''}`;
}

function resetCfgCharTape() {
    cfgVerifiedChars.innerHTML = '';
    setCfgPendingChar(null, 'empty');
}

function prepareCfgCharTape(input) {
    cfgVerifiedChars.innerHTML = '';
    setCfgPendingChar(input.length ? input[0] : null, input.length ? 'pending' : 'empty');
}

function addCfgVerifiedChar(ch) {
    if (ch === null || ch === undefined || ch === '') return;
    const token = document.createElement('span');
    token.className = 'char-token accepted';
    token.textContent = ch;
    cfgVerifiedChars.appendChild(token);
}

function advanceCfgCharTape(input, index) {
    addCfgVerifiedChar(input[index]);
    const next = input[index + 1];
    setCfgPendingChar(next, next === undefined ? 'empty' : 'pending');
}

function showCfgRejectedChar(ch) {
    setCfgPendingChar(ch, 'rejected');
}

function setCfgStringResult(row, valid, value, error) {
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

function resetCfgStringResults() {
    cfgMultiStringRows.forEach(row => {
        const result = row.querySelector('.string-result');
        result.classList.remove('accepted', 'rejected');
        result.classList.add('pending');
        result.textContent = 'Not Checked';
    });
}

async function checkCfgStringRow(row) {
    if (!currentPda) return;
    const input = row.querySelector('.multi-string-input');
    const value = input.value || '';
    setCfgStringResult(row, acceptsSelectedLanguage(value), value, null);
}

async function checkAllCfgStrings() {
    if (!currentPda) return;
    await Promise.all(Array.from(cfgMultiStringRows).map(checkCfgStringRow));
}

// ----------------------------- Marching ants ----------------------------- //

let antsTimer = null;
let antsOffset = 0;

function startAnts() {
    if (antsTimer) return;
    antsTimer = setInterval(() => {
        antsOffset = (antsOffset - 3) % 1000;
        if (!cyPda) return;
        cyPda.edges('.traversing').forEach(e => e.style('line-dash-offset', antsOffset));
    }, 60);
}

function stopAnts() {
    if (antsTimer) {
        clearInterval(antsTimer);
        antsTimer = null;
    }
}

// ----------------------------- Flowchart build ----------------------------- //

function flowNode(id, label, shape, x, y, w = 86, h = 52, classes = '') {
    return { data: { id, label, shape, w, h }, position: { x, y }, classes };
}

function flowEdge(id, source, target, label = '', classes = '') {
    return { data: { id, source, target, label }, classes };
}

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
                'shape': 'data(shape)',
                'width': 'data(w)',
                'height': 'data(h)',
                'text-wrap': 'wrap',
                'text-max-width': 90,
                'transition-property': 'background-color, border-color, border-width, width, height',
                'transition-duration': 180,
            }},
            { selector: 'edge', style: {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': '#8a97a8',
                'target-arrow-color': '#8a97a8',
                'text-rotation': 'none',
                'text-background-color': '#fff',
                'text-background-opacity': 0.9,
                'text-background-padding': 2,
                'font-size': 10,
                'transition-property': 'line-color, target-arrow-color, width',
                'transition-duration': 150,
            }},
            { selector: '.active', style: {
                'background-color': '#e4f5f2',
                'border-color': '#0f766e',
                'border-width': 4,
            }},
            { selector: '.accept', style: {
                'border-width': 6,
                'border-style': 'double',
            }},
            { selector: '.pulse', style: {
                'width': 56,
                'height': 56,
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

function pulseNode(node) {
    if (!node) return;
    node.addClass('pulse');
    setTimeout(() => node.removeClass('pulse'), 280);
}

function edgeById(cy, id) {
    if (!id) return cy.collection();
    return cy.getElementById(id);
}

function addFlowStep(steps, node, edge, text, char = null, rejected = false) {
    steps.push({ node, edge, text, char, rejected });
}

function dfaSpec(index) {
    if (index === 0) {
        return {
            start: 0,
            accept: [10],
            reject: [3],
            states: [
                [0, 80, 210], [1, 210, 110], [2, 210, 310], [3, 340, 210],
                [4, 470, 110], [5, 470, 310], [6, 600, 210], [7, 730, 90],
                [8, 860, 210], [9, 990, 210], [10, 1120, 210],
            ],
            transitions: {
                0: { a: 1, b: 2 },
                1: { a: 3, b: 4 },
                2: { a: 5, b: 3 },
                3: { a: 3, b: 3 },
                4: { a: 6, b: 3 },
                5: { a: 3, b: 6 },
                6: { a: 6, b: 7 },
                7: { a: 8, b: 7 },
                8: { a: 6, b: 9 },
                9: { a: 10, b: 10 },
                10: { a: 10, b: 10 },
            },
        };
    }

    return {
        start: 0,
        accept: [7],
        states: [
            [0, 90, 210], [1, 230, 210], [2, 370, 110], [3, 370, 310],
            [4, 510, 110], [5, 510, 310], [6, 650, 210], [7, 790, 210],
        ],
        transitions: {
            0: { 0: 1, 1: 1 },
            1: { 0: 2, 1: 3 },
            2: { 0: 4, 1: 3 },
            3: { 0: 5, 1: 6 },
            4: { 0: 7, 1: 3 },
            5: { 0: 4, 1: 7 },
            6: { 0: 5, 1: 7 },
            7: { 0: 7, 1: 7 },
        },
    };
}

function acceptsSelectedLanguage(s) {
    const spec = dfaSpec(selectedCfgIndex);
    const rejectStates = new Set(spec.reject || []);
    let state = spec.start;
    for (const ch of s) {
        const next = spec.transitions[state] && spec.transitions[state][ch];
        if (next === undefined) return false;
        if (rejectStates.has(next)) return false;
        state = next;
    }
    return spec.accept.includes(state);
}

function dfaFlowNode(id, label, kind, x, y) {
    if (kind === 'read') return flowNode(id, label, 'diamond', x, y, 92, 62);
    if (kind === 'reject') return flowNode(id, label, 'ellipse', x, y, 100, 44);
    if (kind === 'start' || kind === 'accept') return flowNode(id, label, 'ellipse', x, y, 100, 44);
    return flowNode(id, label, 'roundrectangle', x, y, 96, 44);
}

function buildFlowchartElements(index) {
    const spec = dfaSpec(index);
    const rejectStates = new Set(spec.reject || []);
    const nodes = [
        dfaFlowNode('start', 'START', 'start', spec.states[0][1], 35),
    ];
    const edges = [flowEdge('e_start_read_0', 'start', 'read_0')];

    for (const [state, x, y] of spec.states) {
        const isReject = rejectStates.has(state);
        nodes.push(dfaFlowNode(`read_${state}`, isReject ? 'Reject' : 'READ', isReject ? 'reject' : 'read', x, y));
        if (isReject) continue;

        const trans = spec.transitions[state] || {};
        for (const [symbol, target] of Object.entries(trans)) {
            edges.push(flowEdge(
                `e_read_read_${state}_${symbol}`,
                `read_${state}`,
                `read_${target}`,
                symbol
            ));
        }

        if (spec.accept.includes(state)) {
            nodes.push(dfaFlowNode(`accept_${state}`, 'ACCEPT', 'accept', x, y + 125));
            edges.push(flowEdge(`e_read_accept_${state}`, `read_${state}`, `accept_${state}`, ACCEPT_MARKER));
        }
    }

    return { nodes, edges };
}

function buildFlowSteps(s, valid) {
    const spec = dfaSpec(selectedCfgIndex);
    const rejectStates = new Set(spec.reject || []);
    const steps = [];
    let state = spec.start;

    addFlowStep(steps, 'start', null, 'Start PDA-style READ flow');
    addFlowStep(steps, `read_${state}`, 'e_start_read_0', `Ready at q${state}`);

    for (const ch of s) {
        const next = spec.transitions[state] && spec.transitions[state][ch];
        if (next === undefined) {
            addFlowStep(steps, `read_${state}`, null, `No flow for "${ch}"; REJECT`, ch, true);
            return steps;
        }

        addFlowStep(
            steps,
            `read_${next}`,
            `e_read_read_${state}_${ch}`,
            `Read "${ch}" and move q${state} -> q${next}`,
            ch,
            rejectStates.has(next)
        );
        state = next;
        if (rejectStates.has(state)) return steps;
    }

    if (valid && spec.accept.includes(state)) {
        addFlowStep(steps, `accept_${state}`, `e_read_accept_${state}`, 'Input consumed; ACCEPT');
    } else {
        addFlowStep(steps, `read_${state}`, null, 'Input ended outside an accepting flow; REJECT');
    }
    return steps;
}

function markAcceptNodes() {
    dfaSpec(selectedCfgIndex).accept.forEach(state => {
        cyPda.getElementById(`accept_${state}`).addClass('accept');
    });
}

// ----------------------------- Load selected flow ----------------------------- //

async function loadSelectedCfgFlow() {
    const cfgText = cfgInput.value.trim();
    if (!cfgText) return;

    clearCfgSteps();
    stopAnts();
    addCfgStep('Loading hardcoded PDA flow for the selected regular language...');
    currentPda = { selected: selectedCfgIndex };
    currentSteps = null;
    resetCfgCharTape();

    const els = buildFlowchartElements(selectedCfgIndex);
    if (cyPda) cyPda.destroy();
    cyPda = createCy('cy-pda', els);
    markAcceptNodes();
    resetViewport(cyPda);

    addCfgStep('Compact PDA rendered.');
    await checkAllCfgStrings();
}

// ----------------------------- Run (animate) ----------------------------- //

cfgPauseBtn.addEventListener('click', () => {
    if (cfgPauseBtn.disabled) return;
    setPdaPaused(!pdaPaused);
});

cfgRunBtn.addEventListener('click', async () => {
    if (!currentPda) await loadSelectedCfgFlow();
    const s = document.getElementById('cfg-test-input').value || '';
    await runPda(s);
});

async function runPda(s) {
    const token = ++pdaRunToken;
    setPdaPaused(false);
    setPdaPauseEnabled(true);
    clearCfgSteps();
    addCfgStep('Running hardcoded PDA flow...');
    const valid = acceptsSelectedLanguage(s);
    currentSteps = buildFlowSteps(s, valid);

    cyPda.elements().removeClass('active traversing valid invalid pulse');
    prepareCfgCharTape(s);
    startAnts();

    const delay = 700;
    let currentActiveId = null;
    let consumedIndex = 0;

    try {
        for (let i = 0; i < currentSteps.length; i++) {
            if (!(await waitWhilePdaPaused(token))) return;

            const step = currentSteps[i];

            cyPda.edges('.traversing').removeClass('traversing');
            edgeById(cyPda, step.edge).addClass('traversing');

            if (step.node !== currentActiveId) {
                if (currentActiveId) cyPda.getElementById(currentActiveId).removeClass('active');
                const node = cyPda.getElementById(step.node);
                if (node) node.addClass('active');
                currentActiveId = step.node;
            }
            const activeNode = cyPda.getElementById(step.node);
            if (activeNode) {
                pulseNode(activeNode);
                keepElementInView(cyPda, activeNode);
            }

            if (step.char !== null && step.char !== undefined) {
                if (step.rejected) {
                    showCfgRejectedChar(step.char);
                } else {
                    advanceCfgCharTape(s, consumedIndex);
                }
                consumedIndex += 1;
            }
            addCfgStep(step.text);

            await sleep(delay);
            if (token !== pdaRunToken) return;
        }

        cyPda.edges('.traversing').removeClass('traversing');
        stopAnts();

        if (cyPda) {
            if (valid) cyPda.elements().addClass('valid');
            else cyPda.elements().addClass('invalid');
        }
        addCfgStep(valid ? 'Result: VALID (string accepted)' : 'Result: INVALID (string rejected)');
    } finally {
        if (token === pdaRunToken) setPdaPauseEnabled(false);
    }
}

cfgMultiStringRows.forEach(row => {
    const input = row.querySelector('.multi-string-input');
    const simulateBtn = row.querySelector('.simulate-string-btn');
    input.addEventListener('input', () => checkCfgStringRow(row));
    simulateBtn.addEventListener('click', async () => {
        if (!currentPda) await loadSelectedCfgFlow();
        document.getElementById('cfg-test-input').value = input.value || '';
        await checkCfgStringRow(row);
        scrollPdaVisualizerIntoView();
        await runPda(input.value || '');
    });
});

// ----------------------------- Reset ----------------------------- //

cfgResetBtn.addEventListener('click', async () => {
    cancelPdaRun();
    if (cyPda) cyPda.elements().removeClass('active traversing valid invalid pulse');
    resetViewport(cyPda);
    resetCfgCharTape();
    resetCfgStringResults();
    await checkAllCfgStrings();
    clearCfgSteps();
    addCfgStep('Reset complete. PDA flow is ready.');
});

// Initial state
clearCfgSteps();
showConvertedCfg(0);
