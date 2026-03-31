/*
cfg.js

Frontend logic for the CFG -> PDA page.

Responsibilities:
- Send the CFG text to the backend to construct a PDA
- Render the PDA as a Cytoscape graph
- Request PDA simulation steps for a test string and animate them
- Update a visual stack panel in sync with the animation

All functions include comments to explain expected inputs and DOM effects.
*/

const cfgInput = document.getElementById('cfg-input');
const cfgConvertBtn = document.getElementById('cfg-convert-btn');
const cfgRunBtn = document.getElementById('cfg-run-btn');
const cfgResetBtn = document.getElementById('cfg-reset-btn');
const cfgStepsList = document.getElementById('cfg-steps-list');
const stackContents = document.getElementById('stack-contents');

let cyPda = null;
let currentPda = null;
let currentSteps = null;

async function postJson(url, body) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return res.json();
}

function clearCfgSteps() { cfgStepsList.innerHTML = ''; }
function addCfgStep(text) { const li = document.createElement('li'); li.textContent = text; cfgStepsList.appendChild(li); }

function buildPdaElements(pda) {
    // Nodes: create nodes for each state in pda.states
    const nodes = pda.states.map(s => ({ data: { id: s, label: s } }));
    const edges = [];
    let edgeId = 0;
    for (const t of pda.transitions) {
        const label = `${t.input || 'ε'}, ${t.stack_top} → ${t.push && t.push.length ? t.push.join('') : 'ε'}`;
        edges.push({ data: { id: 'pe' + edgeId++, source: t.from, target: t.to, label: label } });
    }
    return { nodes, edges };
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
                'border-color': '#333',
                'border-width': 2,
                'width': 46,
                'height': 46,
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
            { selector: '.active', style: { 'background-color': '#ffe082', 'border-color': '#ffb300' }},
            { selector: '.valid', style: { 'background-color': '#2e7d32', 'border-color': '#2e7d32', 'line-color': '#2e7d32', 'target-arrow-color': '#2e7d32' }},
            { selector: '.invalid', style: { 'background-color': '#c62828', 'border-color': '#c62828', 'line-color': '#c62828', 'target-arrow-color': '#c62828' }}
        ],
        layout: { name: 'cose', animate: true }
    });
}

function renderStack(stack) {
    // stack is an array where the last element is the top; display top at top visually
    if (!stack || stack.length === 0) {
        stackContents.innerHTML = 'Empty Stack';
        return;
    }
    stackContents.innerHTML = '';
    // Render from bottom to top but visually show reversed (top first)
    const reversed = stack.slice().reverse();
    reversed.forEach((sym, idx) => {
        const div = document.createElement('div');
        div.className = 'stack-box';
        if (idx === 0) div.classList.add('stack-top'); // highlight top
        div.textContent = sym;
        stackContents.appendChild(div);
    });
}

// Convert button builds PDA and renders it
cfgConvertBtn.addEventListener('click', async () => {
    const cfgText = cfgInput.value.trim();
    if (!cfgText) { alert('Please enter CFG rules.'); return; }

    clearCfgSteps();
    addCfgStep('Parsing CFG and constructing PDA...');

    const pdaResp = await postJson('/api/cfg/pda', { cfg: cfgText });
    if (pdaResp.error) { addCfgStep('Error: ' + pdaResp.error); return; }
    currentPda = pdaResp;
    addCfgStep('PDA constructed.');

    // Render PDA
    const els = buildPdaElements(currentPda);
    if (cyPda) cyPda.destroy();
    cyPda = createCy('cy-pda', els);

    addCfgStep('PDA diagram rendered.');
});

// Run button: request simulation steps and animate
cfgRunBtn.addEventListener('click', async () => {
    if (!currentPda) { alert('Please convert CFG first.'); return; }
    const s = document.getElementById('cfg-test-input').value || '';

    clearCfgSteps();
    addCfgStep('Requesting PDA simulation...');

    const res = await postJson('/api/cfg/check', { pda: currentPda, string: s });
    if (res.error) { addCfgStep('Error: ' + res.error); return; }

    currentSteps = res.steps || [];
    const valid = !!res.valid;

    // Animate steps sequentially
    const delay = 600;
    for (let i = 0; i < currentSteps.length; i++) {
        const step = currentSteps[i];
        // Highlight state node
        if (cyPda) cyPda.elements().removeClass('active');
        const node = cyPda ? cyPda.getElementById(step.state) : null;
        if (node) node.addClass('active');

        // Update stack view
        renderStack(step.stack || []);

        // Update step viewer with short description
        addCfgStep(`State: ${step.state}, remaining: "${step.remaining_input}", stack: [${(step.stack||[]).join(',')}]`);

        // wait
        await new Promise(r => setTimeout(r, delay));
    }

    // Final coloring
    if (cyPda) {
        if (valid) cyPda.elements().addClass('valid');
        else cyPda.elements().addClass('invalid');
    }
    addCfgStep(valid ? 'Result: VALID (string accepted)' : 'Result: INVALID (string rejected)');
});

// Reset clears diagram highlights and stack
cfgResetBtn.addEventListener('click', () => {
    if (cyPda) cyPda.elements().removeClass('active valid invalid');
    stackContents.innerHTML = 'Empty Stack';
    clearCfgSteps();
    addCfgStep('Reset complete.');
});

// Initialize
clearCfgSteps();
addCfgStep('Ready. Enter CFG rules and click Convert.');
