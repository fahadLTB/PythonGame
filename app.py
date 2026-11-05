
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="18 Hole Mini Golf",
    page_icon="⛳",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #edf5e9;
}
h1 {
    text-align: center;
    color: #155b36;
}
</style>
""", unsafe_allow_html=True)

st.title("⛳ Ultimate Mini Golf Championship")
st.markdown(
    "<p style='text-align:center;color:#45634d'>"
    "18 Holes | Increasing Difficulty | Championship Mode"
    "</p>",
    unsafe_allow_html=True
)

html_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #edf5e9;
    font-family: Arial, sans-serif;
    color: #183c29;
}

.container {
    max-width: 1050px;
    margin: auto;
    padding: 12px;
}

.top-panel {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 10px;
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
}

.stat {
    text-align: center;
    min-width: 100px;
}

.stat strong {
    display: block;
    font-size: 23px;
    color: #176b3a;
}

.stat span {
    font-size: 13px;
    color: #64786a;
}

.progress {
    height: 12px;
    background: #d5e5d0;
    border-radius: 20px;
    overflow: hidden;
    margin: 12px 0;
}

.progress-fill {
    height: 100%;
    width: 0%;
    background: #198754;
    transition: width .3s;
}

canvas {
    display: block;
    width: 100%;
    border: 4px solid #245c35;
    border-radius: 13px;
    background: #76b85b;
    touch-action: none;
}

.controls {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 15px 0;
}

button {
    border: none;
    background: #176b3a;
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 15px;
    cursor: pointer;
}

button:hover { background: #0d4828; }

button:disabled {
    background: #a5b5a9;
    cursor: not-allowed;
}

#message {
    text-align: center;
    min-height: 28px;
    color: #155b36;
}

.instructions {
    background: white;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 15px;
    line-height: 1.7;
}

.scorecard {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin-top: 15px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    text-align: center;
    font-size: 14px;
}

th, td {
    padding: 9px;
    border-bottom: 1px solid #e3e9e3;
}

th {
    background: #e6f1e4;
}

.current {
    background: #e3f6e8;
    font-weight: bold;
}

.completed {
    color: #16753d;
}

.difficulty {
    text-align: center;
    padding: 8px;
    background: #e6f1e4;
    border-radius: 8px;
    margin-bottom: 10px;
}

@media(max-width:600px) {
    .stat strong { font-size: 18px; }
    button { padding: 10px 13px; }
}
</style>
</head>

<body>

<div class="container">

    <div class="top-panel">

        <div class="stat">
            <strong id="hole">1 / 18</strong>
            <span>Current Hole</span>
        </div>

        <div class="stat">
            <strong id="strokes">0</strong>
            <span>Hole Strokes</span>
        </div>

        <div class="stat">
            <strong id="par">3</strong>
            <span>Hole Par</span>
        </div>

        <div class="stat">
            <strong id="total">0</strong>
            <span>Total Strokes</span>
        </div>

        <div class="stat">
            <strong id="score">E</strong>
            <span>Score vs Par</span>
        </div>

    </div>

    <div class="progress">
        <div class="progress-fill" id="progress"></div>
    </div>

    <div class="difficulty" id="difficulty">
        Difficulty: Beginner
    </div>

    <canvas id="game" width="900" height="500"></canvas>

    <h3 id="message">Welcome! Start your championship.</h3>

    <div class="controls">
        <button onclick="resetHole()">↻ Restart Hole</button>
        <button onclick="nextHole()" id="next" disabled>
            Next Hole →
        </button>
        <button onclick="resetGame()">New Championship</button>
    </div>

    <div class="instructions">
        <b>How to play</b><br>
        1. Click or touch the golf ball.<br>
        2. Drag backwards to aim your shot.<br>
        3. Release to hit the ball.<br>
        4. Avoid water hazards and obstacles.<br>
        5. Complete all 18 holes using the fewest strokes.
        <br><br>
        <b>Scoring:</b> Birdie = one under par | Par = equal to par |
        Bogey = one over par.
    </div>

    <div class="scorecard">

        <h2>🏆 Championship Scorecard</h2>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Hole</th>
                        <th>Par</th>
                        <th>Strokes</th>
                        <th>Result</th>
                    </tr>
                </thead>

                <tbody id="scoreRows"></tbody>

                <tfoot>
                    <tr>
                        <th>TOTAL</th>
                        <th id="totalPar">0</th>
                        <th id="totalTable">0</th>
                        <th id="totalResult">E</th>
                    </tr>
                </tfoot>
            </table>
        </div>

    </div>

</div>

<script>

// =====================================
// GAME CONFIGURATION
// =====================================

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = 900;
const H = 500;

const ballStart = {x: 105, y: 250};

const hole = {
    x: 800,
    y: 250,
    radius: 15
};

let ball = {};
let currentHole = 0;
let strokes = 0;
let scores = Array(18).fill(null);

let dragging = false;
let moving = false;
let won = false;

let mouse = {x: 0, y: 0};

let course = null;

// =====================================
// 18 DIFFERENT LEVELS
// =====================================

function makeCourse(n) {

    let obstacles = [];
    let water = [];
    let sand = [];

    // Difficulty increases every 3 holes.
    const difficulty = Math.floor(n / 3) + 1;

    // Different obstacle arrangements.
    const layouts = [
        [180],
        [240, 500],
        [190, 390],
        [230, 440, 650],
        [180, 350, 530],
        [220, 390, 570],
        [190, 350, 510, 670],
        [230, 400, 570],
        [180, 340, 500, 660],
        [210, 370, 530, 690],
        [190, 330, 470, 610],
        [220, 380, 540, 700],
        [170, 310, 450, 590, 730],
        [210, 350, 490, 630, 740],
        [180, 320, 460, 600, 720],
        [210, 340, 470, 600, 730],
        [170, 300, 430, 560, 690, 750],
        [190, 320, 450, 580, 700, 760]
    ];

    const positions = layouts[n];

    positions.forEach((x, i) => {

        // Each barrier has a different opening.
        let gapCenter = 90 + ((n * 43 + i * 97) % 320);

        let gapSize = Math.max(
            90,
            195 - difficulty * 6
        );

        let topHeight = Math.max(
            35, gapCenter - gapSize / 2
        );

        let bottomY = Math.min(
            465, gapCenter + gapSize / 2
        );

        obstacles.push({
            x: x,
            y: 0,
            w: 17,
            h: topHeight
        });

        obstacles.push({
            x: x,
            y: bottomY,
            w: 17,
            h: 500 - bottomY
        });

    });

    // Water hazards increase with level.
    if (n >= 3) {

        let wx = 300 + (n % 4) * 90;

        water.push({
            x: wx,
            y: n % 2 === 0 ? 30 : 350,
            w: 90,
            h: 105
        });
    }

    if (n >= 7) {

        water.push({
            x: 570,
            y: n % 2 === 0 ? 360 : 35,
            w: 85,
            h: 90
        });
    }

    if (n >= 13) {

        water.push({
            x: 690,
            y: n % 2 === 0 ? 45 : 365,
            w: 65,
            h: 80
        });
    }

    // Sand traps.
    if (n >= 2) {
        sand.push({
            x: 430,
            y: n % 2 === 0 ? 390 : 80,
            rx: 55,
            ry: 40
        });
    }

    if (n >= 10) {
        sand.push({
            x: 650,
            y: n % 2 === 0 ? 110 : 390,
            rx: 42,
            ry: 32
        });
    }

    const pars = [
        3,3,3,3,4,3,4,4,4,
        4,4,4,4,5,4,5,5,5
    ];

    return {
        obstacles,
        water,
        sand,
        par: pars[n],
        difficulty
    };
}

// =====================================
// INITIALIZE HOLE
// =====================================

function loadHole() {

    course = makeCourse(currentHole);

    ball = {
        x: ballStart.x,
        y: ballStart.y,
        vx: 0,
        vy: 0,
        radius: 9
    };

    strokes = 0;
    dragging = false;
    moving = false;
    won = false;

    document.getElementById("hole").innerText =
        (currentHole + 1) + " / 18";

    document.getElementById("strokes").innerText = 0;

    document.getElementById("par").innerText =
        course.par;

    document.getElementById("difficulty").innerText =
        "Difficulty: " + getDifficulty(course.difficulty);

    document.getElementById("message").innerText =
        "Hole " + (currentHole + 1) +
        " — Aim and take your shot!";

    document.getElementById("next").disabled = true;

    updateScoreboard();
}

function getDifficulty(d) {

    if(d <= 1) return "Beginner";
    if(d <= 2) return "Easy";
    if(d <= 3) return "Intermediate";
    if(d <= 4) return "Advanced";
    if(d <= 5) return "Expert";
    return "Championship";
}

// =====================================
// DRAW GOLF COURSE
// =====================================

function drawCourse() {

    ctx.fillStyle = "#77b95c";
    ctx.fillRect(0, 0, W, H);

    // Grass stripes.
    for(let i = 0; i < 9; i++) {

        ctx.fillStyle = i % 2 === 0
            ? "#7fc267" : "#70ad53";

        ctx.fillRect(i * 100, 0, 100, H);
    }

    // Boundary.
    ctx.strokeStyle = "#e5f3db";
    ctx.lineWidth = 7;
    ctx.strokeRect(5, 5, W - 10, H - 10);

    // Sand traps.
    course.sand.forEach(s => {

        ctx.fillStyle = "#e5c77f";

        ctx.beginPath();
        ctx.ellipse(
            s.x, s.y, s.rx, s.ry,
            0, 0, Math.PI * 2
        );
        ctx.fill();

        ctx.strokeStyle = "#c6a85e";
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    // Water hazards.
    course.water.forEach(w => {

        ctx.fillStyle = "#299bc9";
        ctx.fillRect(w.x, w.y, w.w, w.h);

        ctx.strokeStyle = "#b4e7f5";
        ctx.lineWidth = 3;
        ctx.strokeRect(w.x, w.y, w.w, w.h);

        ctx.fillStyle = "white";
        ctx.font = "15px Arial";
        ctx.fillText("WATER", w.x + 10, w.y + 25);
    });

    // Obstacles.
    course.obstacles.forEach(o => {

        ctx.fillStyle = "#75502f";
        ctx.fillRect(o.x, o.y, o.w, o.h);

        ctx.fillStyle = "#aa8054";
        ctx.fillRect(o.x + 4, o.y, 5, o.h);
    });

    // Hole.
    ctx.fillStyle = "#222";
    ctx.beginPath();
    ctx.arc(hole.x, hole.y, hole.radius, 0, Math.PI * 2);
    ctx.fill();

    // Flag.
    ctx.strokeStyle = "white";
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(hole.x, hole.y);
    ctx.lineTo(hole.x, hole.y - 65);
    ctx.stroke();

    ctx.fillStyle = "#e63946";

    ctx.beginPath();
    ctx.moveTo(hole.x, hole.y - 65);
    ctx.lineTo(hole.x + 35, hole.y - 53);
    ctx.lineTo(hole.x, hole.y - 42);
    ctx.fill();

    // Starting position marker.
    ctx.fillStyle = "white";
    ctx.font = "13px Arial";
    ctx.fillText("START", 75, 285);
}

// =====================================
// DRAW BALL
// =====================================

function drawBall() {

    ctx.fillStyle = "rgba(0,0,0,0.2)";

    ctx.beginPath();
    ctx.ellipse(
        ball.x + 3, ball.y + 5,
        10, 5, 0, 0, Math.PI * 2
    );
    ctx.fill();

    ctx.fillStyle = "white";

    ctx.beginPath();
    ctx.arc(
        ball.x, ball.y,
        ball.radius, 0, Math.PI * 2
    );
    ctx.fill();

    ctx.strokeStyle = "#aaa";
    ctx.stroke();
}

// =====================================
// AIMING
// =====================================

function drawAim() {

    if(!dragging) return;

    const dx = ball.x - mouse.x;
    const dy = ball.y - mouse.y;

    const power = Math.min(
        100,
        Math.sqrt(dx * dx + dy * dy) / 2
    );

    ctx.strokeStyle = "#ffeb3b";
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(ball.x, ball.y);
    ctx.lineTo(ball.x + dx, ball.y + dy);
    ctx.stroke();

    ctx.fillStyle = "white";
    ctx.font = "18px Arial";

    ctx.fillText(
        "Power: " + Math.round(power) + "%",
        20, 35
    );
}

// =====================================
// COLLISION DETECTION
// =====================================

function collideRectangle(o) {

    let cx = Math.max(
        o.x,
        Math.min(ball.x, o.x + o.w)
    );

    let cy = Math.max(
        o.y,
        Math.min(ball.y, o.y + o.h)
    );

    let dx = ball.x - cx;
    let dy = ball.y - cy;

    let distance = Math.sqrt(dx * dx + dy * dy);

    if(distance < ball.radius) {

        if(Math.abs(dx) > Math.abs(dy)) {

            ball.vx *= -0.65;
            ball.x += dx >= 0 ? 3 : -3;

        } else {

            ball.vy *= -0.65;
            ball.y += dy >= 0 ? 3 : -3;
        }
    }
}

function checkCollisions() {

    // Walls.
    if(ball.x < 15 || ball.x > 885) {

        ball.vx *= -0.65;
        ball.x = Math.max(15, Math.min(885, ball.x));
    }

    if(ball.y < 15 || ball.y > 485) {

        ball.vy *= -0.65;
        ball.y = Math.max(15, Math.min(485, ball.y));
    }

    // Obstacles.
    course.obstacles.forEach(collideRectangle);

    // Water hazard penalty.
    for(let w of course.water) {

        let cx = Math.max(
            w.x, Math.min(ball.x, w.x + w.w)
        );

        let cy = Math.max(
            w.y, Math.min(ball.y, w.y + w.h)
        );

        let dx = ball.x - cx;
        let dy = ball.y - cy;

        if(dx * dx + dy * dy < ball.radius * ball.radius) {

            strokes++;

            ball.x = ballStart.x;
            ball.y = ballStart.y;
            ball.vx = 0;
            ball.vy = 0;

            moving = false;

            document.getElementById("message").innerText =
                "💧 Water hazard! One penalty stroke added. Try again.";

            document.getElementById("strokes").innerText =
                strokes;

            return;
        }
    }
}

// =====================================
// SAND FRICTION
// =====================================

function onSand() {

    return course.sand.some(s => {

        const dx = (ball.x - s.x) / s.rx;
        const dy = (ball.y - s.y) / s.ry;

        return dx * dx + dy * dy <= 1;
    });
}

// =====================================
// CHECK HOLE
// =====================================

function checkHole() {

    const dx = hole.x - ball.x;
    const dy = hole.y - ball.y;

    const distance = Math.sqrt(dx * dx + dy * dy);

    const speed = Math.sqrt(
        ball.vx * ball.vx + ball.vy * ball.vy
    );

    if(distance < hole.radius && speed < 1.8) {

        ball.x = hole.x;
        ball.y = hole.y;
        ball.vx = 0;
        ball.vy = 0;

        moving = false;
        won = true;

        scores[currentHole] = strokes;

        const difference = strokes - course.par;

        let result = "Par!";

        if(difference <= -2) result = "Eagle!";
        else if(difference === -1) result = "Birdie!";
        else if(difference === 1) result = "Bogey!";
        else if(difference === 2) result = "Double Bogey!";

        document.getElementById("message").innerText =
            "🏆 Hole completed! " + result +
            " Strokes: " + strokes +
            " | Par: " + course.par;

        document.getElementById("next").disabled = false;

        if(currentHole === 17) {

            document.getElementById("message").innerText =
                "🏆 CHAMPIONSHIP COMPLETED! Check your final scorecard!";

        }

        updateScoreboard();
    }
}

// =====================================
// GAME PHYSICS
// =====================================

function update() {

    if(won) return;

    ball.x += ball.vx;
    ball.y += ball.vy;

    const friction = onSand() ? 0.94 : 0.985;

    ball.vx *= friction;
    ball.vy *= friction;

    if(Math.abs(ball.vx) < 0.04) ball.vx = 0;
    if(Math.abs(ball.vy) < 0.04) ball.vy = 0;

    checkCollisions();

    moving = Math.abs(ball.vx) > 0 ||
             Math.abs(ball.vy) > 0;

    if(!moving) {
        checkHole();
    }
}

// =====================================
// MAIN GAME LOOP
// =====================================

function draw() {

    ctx.clearRect(0, 0, W, H);

    drawCourse();
    drawBall();
    drawAim();

    update();

    requestAnimationFrame(draw);
}

// =====================================
// MOUSE AND TOUCH CONTROLS
// =====================================

function getPosition(e) {

    const rect = canvas.getBoundingClientRect();

    return {
        x: (e.clientX - rect.left) * W / rect.width,
        y: (e.clientY - rect.top) * H / rect.height
    };
}

canvas.addEventListener("pointerdown", e => {

    if(won || moving) return;

    const p = getPosition(e);

    const dx = p.x - ball.x;
    const dy = p.y - ball.y;

    if(Math.sqrt(dx * dx + dy * dy) < 35) {

        dragging = true;
        mouse = p;

        canvas.setPointerCapture(e.pointerId);
    }
});

canvas.addEventListener("pointermove", e => {

    if(!dragging) return;

    mouse = getPosition(e);
});

canvas.addEventListener("pointerup", () => {

    if(!dragging) return;

    const dx = ball.x - mouse.x;
    const dy = ball.y - mouse.y;

    const power = Math.sqrt(dx * dx + dy * dy);

    if(power > 5) {

        const scale = Math.min(power, 200) / 200;

        ball.vx = dx * scale * 0.11;
        ball.vy = dy * scale * 0.11;

        strokes++;

        document.getElementById("strokes").innerText =
            strokes;

        document.getElementById("message").innerText =
            "⛳ Ball in motion!";
    }

    dragging = false;
});

// =====================================
// SCOREBOARD
// =====================================

function formatScore(difference) {

    if(difference === null) return "—";
    if(difference <= -3) return "Albatross";
    if(difference === -2) return "Eagle";
    if(difference === -1) return "Birdie";
    if(difference === 0) return "Par";
    if(difference === 1) return "Bogey";
    if(difference === 2) return "Double Bogey";

    return "+" + difference;
}

function updateScoreboard() {

    const rows = document.getElementById("scoreRows");

    rows.innerHTML = "";

    let totalPar = 0;
    let totalStrokes = 0;

    for(let i = 0; i < 18; i++) {

        const par = makeCourse(i).par;
        const score = scores[i];

        totalPar += par;

        if(score !== null) {
            totalStrokes += score;
        }

        const tr = document.createElement("tr");

        if(i === currentHole) tr.className = "current";

        const result = score === null
            ? "—"
            : formatScore(score - par);

        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${par}</td>
            <td>${score === null ? "—" : score}</td>
            <td>${result}</td>
        `;

        rows.appendChild(tr);
    }

    let completedPar = 0;

    for(let i = 0; i < 18; i++) {
        if(scores[i] !== null) {
            completedPar += makeCourse(i).par;
        }
    }

    const difference = totalStrokes - completedPar;

    const scoreText = difference > 0
        ? "+" + difference
        : difference === 0 ? "E" : difference;

    document.getElementById("total").innerText =
        totalStrokes;

    document.getElementById("score").innerText =
        scores.every(s => s !== null) ? scoreText : "—";

    document.getElementById("totalPar").innerText =
        totalPar;

    document.getElementById("totalTable").innerText =
        totalStrokes;

    document.getElementById("totalResult").innerText =
        scores.every(s => s !== null) ? scoreText : "—";

    const completed = scores.filter(s => s !== null).length;

    document.getElementById("progress").style.width =
        (completed / 18 * 100) + "%";
}

// =====================================
// NEXT HOLE
// =====================================

function nextHole() {

    if(!won) return;

    if(currentHole < 17) {

        currentHole++;
        loadHole();

    } else {

        document.getElementById("message").innerText =
            "🏆 You finished all 18 holes! Final score: " +
            scores.reduce((a, b) => a + b, 0) +
            " strokes.";
    }
}

// =====================================
// RESTART
// =====================================

function resetHole() {

    scores[currentHole] = null;
    loadHole();
}

function resetGame() {

    currentHole = 0;
    scores = Array(18).fill(null);

    loadHole();
}

// START
loadHole();
draw();

</script>
</body>
</html>
"""

components.html(
    html_code,
    height=1250,
    scrolling=True
)

st.markdown("---")

st.markdown("""
<div style="text-align:center;color:#56705c">
    <b>18 Hole Mini Golf Championship</b><br>
    Built with Python + Streamlit + HTML + CSS + JavaScript
</div>
""", unsafe_allow_html=True)
