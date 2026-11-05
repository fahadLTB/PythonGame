
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Mini Golf Game",
    page_icon="⛳",
    layout="wide"
)

# -------------------------------
# Streamlit UI
# -------------------------------

st.markdown("""
<style>
.main {
    background-color: #f0f5ed;
}
h1 {
    color: #155b36;
    text-align: center;
}
.game-info {
    text-align: center;
    color: #45634d;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

st.title("⛳ Mini Golf Challenge")

st.markdown(
    '<p class="game-info">Aim carefully, control your power, '
    'and get the ball into the hole!</p>',
    unsafe_allow_html=True
)

# -------------------------------
# HTML + CSS + JavaScript Game
# -------------------------------

html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #e9f5e5;
}

.game-container {
    max-width: 950px;
    margin: auto;
    text-align: center;
    padding: 12px;
}

canvas {
    width: 100%;
    max-width: 900px;
    border: 4px solid #245c35;
    border-radius: 14px;
    background: #76b85b;
    cursor: crosshair;
    touch-action: none;
}

.controls {
    background: white;
    padding: 15px;
    margin-top: 12px;
    border-radius: 12px;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 12px;
}

button {
    padding: 12px 25px;
    border: none;
    border-radius: 8px;
    background: #176b3a;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #0c4826;
}

.info {
    font-size: 18px;
    font-weight: bold;
    color: #174b2c;
}

.instructions {
    background: white;
    padding: 12px;
    border-radius: 10px;
    margin-top: 12px;
    color: #34523b;
}
</style>
</head>

<body>

<div class="game-container">

    <h2>🏌️ Welcome to Mini Golf</h2>

    <canvas id="golfCanvas"
            width="900"
            height="500">
    </canvas>

    <div class="controls">

        <div class="info">
            Strokes: <span id="strokes">0</span>
        </div>

        <div class="info">
            Par: 3
        </div>

        <div class="info">
            Power: <span id="power">0</span>%
        </div>

        <button onclick="resetGame()">
            🔄 Restart
        </button>

    </div>

    <div class="instructions">
        <b>How to play:</b><br>
        1. Click or touch the golf ball.<br>
        2. Drag away from the direction you want to shoot.<br>
        3. Release to hit the ball.<br>
        4. Get the ball into the hole with the fewest strokes!
    </div>

    <h3 id="message">Ready to play!</h3>

</div>

<script>

const canvas = document.getElementById("golfCanvas");
const ctx = canvas.getContext("2d");

let ball = {
    x: 110,
    y: 250,
    vx: 0,
    vy: 0,
    radius: 9
};

const hole = {
    x: 790,
    y: 250,
    radius: 15
};

let strokes = 0;
let dragging = false;
let aimX = 0;
let aimY = 0;
let mouseX = 0;
let mouseY = 0;
let moving = false;
let gameWon = false;

const obstacles = [
    {x: 340, y: 155, w: 28, h: 190},
    {x: 560, y: 0, w: 25, h: 165},
    {x: 560, y: 335, w: 25, h: 165}
];

const sandTrap = {
    x: 420,
    y: 355,
    w: 115,
    h: 85
};

function drawCourse() {

    // Grass
    ctx.fillStyle = "#76b85b";
    ctx.fillRect(0, 0, 900, 500);

    // Grass stripes
    for(let i=0; i<9; i++) {
        ctx.fillStyle = i % 2 === 0
            ? "#7fc267" : "#70ae53";
        ctx.fillRect(i*100, 0, 100, 500);
    }

    // Course boundary
    ctx.strokeStyle = "#e4f1d9";
    ctx.lineWidth = 7;
    ctx.strokeRect(5, 5, 890, 490);

    // Sand trap
    ctx.fillStyle = "#dfc47e";
    ctx.beginPath();
    ctx.ellipse(
        477, 398, 58, 43, 0, 0, Math.PI*2
    );
    ctx.fill();

    // Obstacles
    obstacles.forEach(o => {
        ctx.fillStyle = "#65472e";
        ctx.fillRect(o.x, o.y, o.w, o.h);

        ctx.fillStyle = "#92714b";
        ctx.fillRect(o.x+5, o.y, 7, o.h);
    });

    // Hole
    ctx.fillStyle = "#222";
    ctx.beginPath();
    ctx.arc(
        hole.x, hole.y, hole.radius, 0, Math.PI*2
    );
    ctx.fill();

    // Flag pole
    ctx.strokeStyle = "white";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(hole.x, hole.y);
    ctx.lineTo(hole.x, hole.y-65);
    ctx.stroke();

    ctx.fillStyle = "#e63946";
    ctx.beginPath();
    ctx.moveTo(hole.x, hole.y-65);
    ctx.lineTo(hole.x+35, hole.y-53);
    ctx.lineTo(hole.x, hole.y-42);
    ctx.fill();
}

function drawBall() {

    // Shadow
    ctx.fillStyle = "rgba(0,0,0,0.2)";
    ctx.beginPath();
    ctx.ellipse(
        ball.x+3, ball.y+5,
        10, 5, 0, 0, Math.PI*2
    );
    ctx.fill();

    // Ball
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc(
        ball.x, ball.y,
        ball.radius, 0, Math.PI*2
    );
    ctx.fill();

    ctx.strokeStyle = "#bbb";
    ctx.lineWidth = 1;
    ctx.stroke();
}

function drawAim() {

    if(!dragging) return;

    const dx = ball.x - mouseX;
    const dy = ball.y - mouseY;

    const power = Math.min(
        100, Math.sqrt(dx*dx + dy*dy) / 2
    );

    ctx.strokeStyle = "#ffeb3b";
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(ball.x, ball.y);
    ctx.lineTo(
        ball.x + dx,
        ball.y + dy
    );
    ctx.stroke();

    ctx.fillStyle = "#ffeb3b";
    ctx.font = "16px Arial";
    ctx.fillText(
        "Power: " + Math.round(power) + "%",
        20, 35
    );

    document.getElementById("power").innerText =
        Math.round(power);
}

function checkCollision() {

    // Wall collision
    if(ball.x < 15 || ball.x > 885) {
        ball.vx *= -0.65;
        ball.x = Math.max(15, Math.min(885, ball.x));
    }

    if(ball.y < 15 || ball.y > 485) {
        ball.vy *= -0.65;
        ball.y = Math.max(15, Math.min(485, ball.y));
    }

    // Obstacle collision
    obstacles.forEach(o => {

        const closestX = Math.max(
            o.x, Math.min(ball.x, o.x+o.w)
        );

        const closestY = Math.max(
            o.y, Math.min(ball.y, o.y+o.h)
        );

        const dx = ball.x - closestX;
        const dy = ball.y - closestY;

        if(dx*dx + dy*dy < ball.radius*ball.radius) {

            if(Math.abs(dx) > Math.abs(dy)) {
                ball.vx *= -0.7;
                ball.x += Math.sign(dx || 1)*3;
            } else {
                ball.vy *= -0.7;
                ball.y += Math.sign(dy || 1)*3;
            }
        }
    });

}

function checkHole() {

    const dx = hole.x - ball.x;
    const dy = hole.y - ball.y;
    const distance = Math.sqrt(dx*dx + dy*dy);

    if(distance < hole.radius &&
       Math.sqrt(ball.vx**2 + ball.vy**2) < 2.2) {

        ball.x = hole.x;
        ball.y = hole.y;
        ball.vx = 0;
        ball.vy = 0;
        gameWon = true;

        document.getElementById("message").innerText =
            "🎉 Congratulations! You completed the hole in "
            + strokes + " strokes!";
    }
}

function update() {

    if(gameWon) return;

    ball.x += ball.vx;
    ball.y += ball.vy;

    ball.vx *= 0.985;
    ball.vy *= 0.985;

    if(Math.abs(ball.vx) < 0.04) ball.vx = 0;
    if(Math.abs(ball.vy) < 0.04) ball.vy = 0;

    checkCollision();
    checkHole();

    moving = Math.abs(ball.vx) > 0 ||
             Math.abs(ball.vy) > 0;
}

function draw() {

    ctx.clearRect(0, 0, 900, 500);

    drawCourse();
    drawBall();
    drawAim();

    update();

    requestAnimationFrame(draw);
}

function getPosition(e) {

    const rect = canvas.getBoundingClientRect();

    return {
        x: (e.clientX - rect.left) *
           canvas.width / rect.width,

        y: (e.clientY - rect.top) *
           canvas.height / rect.height
    };
}

canvas.addEventListener("pointerdown", function(e) {

    if(gameWon || moving) return;

    const pos = getPosition(e);

    const dx = pos.x - ball.x;
    const dy = pos.y - ball.y;

    if(Math.sqrt(dx*dx + dy*dy) < 35) {

        dragging = true;
        mouseX = pos.x;
        mouseY = pos.y;

        canvas.setPointerCapture(e.pointerId);
    }

});

canvas.addEventListener("pointermove", function(e) {

    if(!dragging) return;

    const pos = getPosition(e);

    mouseX = pos.x;
    mouseY = pos.y;

});

canvas.addEventListener("pointerup", function() {

    if(!dragging) return;

    const dx = ball.x - mouseX;
    const dy = ball.y - mouseY;

    const power = Math.sqrt(dx*dx + dy*dy);

    if(power > 5) {

        const scale = Math.min(power, 200) / 200;

        ball.vx = dx * scale * 0.11;
        ball.vy = dy * scale * 0.11;

        strokes++;

        document.getElementById("strokes").innerText =
            strokes;

        document.getElementById("message").innerText =
            "Good shot! Keep going!";
    }

    dragging = false;
    document.getElementById("power").innerText = 0;

});

function resetGame() {

    ball.x = 110;
    ball.y = 250;
    ball.vx = 0;
    ball.vy = 0;

    strokes = 0;
    dragging = false;
    moving = false;
    gameWon = false;

    document.getElementById("strokes").innerText = 0;
    document.getElementById("power").innerText = 0;

    document.getElementById("message").innerText =
        "Ready to play!";

}

draw();

</script>

</body>
</html>
"""

# Display the HTML game inside Streamlit
components.html(
    html_code,
    height=750,
    scrolling=True
)

st.markdown("---")
st.caption("Mini Golf Game | Built with Python + Streamlit + HTML + CSS + JavaScript")
