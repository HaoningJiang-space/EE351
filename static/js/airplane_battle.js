document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    const playerImg = new Image();
    playerImg.src = '/static/images/player.png'; // 修改为绝对路径
    // Define supported audio formats
    const audioFormats = [
        { mime: 'audio/mpeg', src: '/static/audio/background_music.mp3' }, // MP3
        { mime: 'audio/ogg', src: '/static/audio/background_music.ogg' }, // OGG
        { mime: 'audio/wav', src: '/static/audio/background_music.wav' }, // WAV
        { mime: 'audio/mp4', src: '/static/audio/background_music.m4a' }, // M4A
    ];

    // Function: Get supported audio source
    function getSupportedAudioSource(formats) {
        const audio = new Audio();
        for (let format of formats) {
            const canPlay = audio.canPlayType(format.mime);
            if (canPlay === 'probably' || canPlay === 'maybe') {
                return format.src;
            }
        }
        return null;
    }

    // Get supported audio source
    const supportedAudioSrc = getSupportedAudioSource(audioFormats);

    // Create background music object
    let backgroundMusic = null;
    if (supportedAudioSrc) {
        backgroundMusic = new Audio(supportedAudioSrc);
        backgroundMusic.loop = true;
        backgroundMusic.volume = 0.5;
    } else {
        console.error('The current browser does not support any of the provided audio formats.');
    }

    // Game parameters
    const GAME_WIDTH = canvas.width;
    const GAME_HEIGHT = canvas.height;
    let score = 0;
    let lives = 3;
    let gameOver = false;
    let gameStarted = false;

    // Background stars
    const stars = [];
    const numStars = 100;

    // Initialize stars
    for (let i = 0; i < numStars; i++) {
        stars.push({
            x: Math.random() * GAME_WIDTH,
            y: Math.random() * GAME_HEIGHT,
            radius: Math.random() * 2,
            speed: Math.random() * 1 + 0.5
        });
    }

    // Player airplane object
    const player = {
        x: GAME_WIDTH / 2 - 20,
        y: GAME_HEIGHT - 80,
        width: 40,
        height: 40,
        speed: 5,
        dx: 0,
        dy: 0,
        color: 'blue',
        bullets: []
    };

    // Enemies array
    const enemies = [];

    // Bullet class
    class Bullet {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.width = 5;
            this.height = 15;
            this.speed = 7;
            this.color = 'yellow';
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }

        update() {
            this.y -= this.speed;
        }

        isOffScreen() {
            return this.y + this.height < 0;
        }
    }

    // Enemy class
    class Enemy {
        constructor() {
            this.width = Math.random() * 30 + 20;
            this.height = Math.random() * 30 + 20;
            this.x = Math.random() * (GAME_WIDTH - this.width);
            this.y = -this.height;
            this.speed = Math.random() * 2 + 1;
            this.color = 'red';
        }

        draw() {
            // Draw a more complex triangular enemy
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.moveTo(this.x + this.width / 2, this.y);
            ctx.lineTo(this.x, this.y + this.height);
            ctx.lineTo(this.x + this.width, this.y + this.height);
            ctx.lineTo(this.x + this.width / 2, this.y + this.height / 2);
            ctx.closePath();
            ctx.fill();
        }

        update() {
            this.y += this.speed;
        }

        isOffScreen() {
            return this.y > GAME_HEIGHT;
        }
    }

    // Draw background stars
    function drawStars() {
        ctx.fillStyle = 'white';
        stars.forEach(star => {
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    // Update and draw background stars
    function updateStars() {
        stars.forEach(star => {
            star.y += star.speed;
            if (star.y > GAME_HEIGHT) {
                star.y = 0;
                star.x = Math.random() * GAME_WIDTH;
            }
        });
    }

    // Draw player airplane
    function drawPlayer() {
        if (playerImg.complete) { // Ensure image is loaded
            ctx.drawImage(playerImg, player.x, player.y, player.width, player.height);
        } else {
            // Draw alternative shape
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.moveTo(player.x + player.width / 2, player.y);
            ctx.lineTo(player.x, player.y + player.height);
            ctx.lineTo(player.x + player.width, player.y + player.height);
            ctx.lineTo(player.x + player.width / 2, player.y + player.height / 2);
            ctx.closePath();
            ctx.fill();
        }
    }

    // Draw bullets
    function drawBullets() {
        player.bullets.forEach((bullet, index) => {
            bullet.draw();
            bullet.update();
            // Remove bullets that are off the canvas
            if (bullet.isOffScreen()) {
                player.bullets.splice(index, 1);
            }
        });
    }

    // Draw enemies
    function drawEnemies() {
        enemies.forEach((enemy, index) => {
            enemy.draw();
            enemy.update();

            // Collision detection (enemy with player)
            if (
                player.x < enemy.x + enemy.width &&
                player.x + player.width > enemy.x &&
                player.y < enemy.y + enemy.height &&
                player.y + player.height > enemy.y
            ) {
                enemies.splice(index, 1);
                lives--;
                if (lives <= 0) {
                    gameOver = true;
                }
            }

            // Collision detection (bullet with enemy)
            player.bullets.forEach((bullet, bIndex) => {
                if (
                    bullet.x < enemy.x + enemy.width &&
                    bullet.x + bullet.width > enemy.x &&
                    bullet.y < enemy.y + enemy.height &&
                    bullet.y + bullet.height > enemy.y
                ) {
                    // Remove bullet and enemy
                    player.bullets.splice(bIndex, 1);
                    enemies.splice(index, 1);
                    score += 10;
                }
            });

            // Remove enemies that are off the canvas
            if (enemy.isOffScreen()) {
                enemies.splice(index, 1);
            }
        });
    }

    // Shoot bullet
    function shoot() {
        const bullet = new Bullet(player.x + player.width / 2 - 2.5, player.y);
        player.bullets.push(bullet);
    }

    // Generate enemy
    function generateEnemy() {
        if (!gameOver) {
            enemies.push(new Enemy());
        }
    }

    // Display score and lives
    function drawHUD() {
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.fillText(`Score: ${score}`, 10, 30);
        ctx.fillText(`Lives: ${lives}`, GAME_WIDTH - 100, 30);
    }

    // Show game over screen
    function showGameOver() {
        // Create game over overlay
        const overlay = document.createElement('div');
        overlay.id = 'gameOverOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.color = 'white';
        overlay.style.zIndex = '1000';
        overlay.innerHTML = `
            <h1>Game Over!</h1>
            <p>Your Score: ${score}</p>
            <button id="restartButton">Restart</button>
        `;

        // Add overlay to the page
        document.body.appendChild(overlay);

        // Add click event to restart button
        const restartButton = document.getElementById('restartButton');
        restartButton.addEventListener('click', restartGame);

        // Pause background music
        if (backgroundMusic) {
            backgroundMusic.pause();
        }
    }

    // Restart game
    function restartGame() {
        // Reset game parameters
        score = 0;
        lives = 3;
        gameOver = false;
        enemies.length = 0; // Clear enemies array
        player.bullets = []; // Clear bullets array
        player.x = GAME_WIDTH / 2 - 20;
        player.y = GAME_HEIGHT - 80;

        // Remove game over overlay
        const overlay = document.getElementById('gameOverOverlay');
        if (overlay) {
            overlay.remove();
        }

        // Restart background music
        if (backgroundMusic) {
            backgroundMusic.currentTime = 0;
            backgroundMusic.play().catch(error => {
                console.error('Failed to play background music:', error);
            });
        }

        // Restart game loop
        update();
    }

    // Show start screen
    function showStartScreen() {
        const overlay = document.createElement('div');
        overlay.id = 'startOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.color = 'white';
        overlay.style.zIndex = '1000';
        overlay.innerHTML = `
            <h1>Welcome to Airplane Battle Game</h1>
            <p>Control your airplane to dodge and shoot enemies.</p>
            <ul style="text-align: left; max-width: 400px;">
                <li><strong>← / →</strong> : Move Left/Right</li>
                <li><strong>↑ / ↓</strong> : Move Up/Down</li>
                <li><strong>Enter</strong> : Shoot Bullets</li>
            </ul>
            <button id="startButton">Start Game</button>
        `;

        // Add overlay to the page
        document.body.appendChild(overlay);

        // Add click event to start button
        const startButton = document.getElementById('startButton');
        startButton.addEventListener('click', () => {
            overlay.remove();
            gameStarted = true;
            if (backgroundMusic) {
                backgroundMusic.play().catch(error => {
                    console.error('Failed to play background music:', error);
                });
            }
            update();
        });
    }

    // Clear canvas
    function clear() {
        ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
    }

    // Update player position
    function newPos() {
        player.x += player.dx;
        player.y += player.dy;

        // Boundary detection
        if (player.x < 0) player.x = 0;
        if (player.x + player.width > GAME_WIDTH) player.x = GAME_WIDTH - player.width;
        if (player.y < 0) player.y = 0;
        if (player.y + player.height > GAME_HEIGHT) player.y = GAME_HEIGHT - player.height;
    }

    // Update game frame
    function update() {
        clear();
        drawStars();
        updateStars();
        drawPlayer();
        drawBullets();
        newPos();
        drawEnemies();
        drawHUD();

        if (gameOver) {
            showGameOver();
            return;
        }

        requestAnimationFrame(update);
    }

    // Key down event
    function keyDown(e) {
        switch (e.key) {
            case 'ArrowRight':
            case 'Right':
                player.dx = player.speed;
                break;
            case 'ArrowLeft':
            case 'Left':
                player.dx = -player.speed;
                break;
            case 'ArrowUp':
            case 'Up':
                player.dy = -player.speed;
                break;
            case 'ArrowDown':
            case 'Down':
                player.dy = player.speed;
                break;
            case 'Enter':
                shoot();
                break;
        }
    }

    // Key up event
    function keyUp(e) {
        switch (e.key) {
            case 'ArrowRight':
            case 'Right':
            case 'ArrowLeft':
            case 'Left':
                player.dx = 0;
                break;
            case 'ArrowUp':
            case 'Up':
            case 'ArrowDown':
            case 'Down':
                player.dy = 0;
                break;
        }
    }

    // Listen to keyboard events 
    document.addEventListener('keydown', keyDown);
    document.addEventListener('keyup', keyUp);

    // Generate an enemy every 1.5 seconds
    setInterval(generateEnemy, 1500);

    // Show start screen
    showStartScreen();
});