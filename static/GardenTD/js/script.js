const canvas = document.querySelector('canvas')
const c = canvas.getContext('2d')
//define canvas dimensions
canvas.width = 1024
canvas.height = 512
//white rectangle of canvas dimensions
c.fillStyle = 'white'
c.fillRect(0, 0, canvas.width, canvas.height)

let animationId = null;
//********************************************************************************** 

//placement tiles rows
const placementTilesData2D = []

//iterates through placementTilesData.js
for (let i = 0; i < placementTilesData.length; i+= 64) { //20 elements per row
    placementTilesData2D.push(placementTilesData.slice(i, i + 64))
}

//define our placement tile array
const placementTiles = []

//Scan placement tile array data placementTilesData.js
placementTilesData2D.forEach((row, y) => {
    row.forEach((symbol, x) => {
        if (symbol != 0) {
            //add building placement tile here
            placementTiles.push(
                new PlacementTile({
                position: {
                    x: x * 16, //64
                    y: y * 16  //64
                }
            }))
        }
    })
})
//********************************************************************************** 
function startLoop() {
  if (animationID !== null || isPaused || isGameOver) return; // already running or should not run
  animationID = requestAnimationFrame(animate);
}
function stopLoop() {
  if (animationID !== null) {
    cancelAnimationFrame(animationID);
    animationID = null;
  }
}
//instantiate our map image
const image = new Image();
let imageReady = false;
image.onload = () => {
  imageReady = true;
  console.log('Map image ready');
};
image.src = '/static/GardenTD/img/gameMap.png'; //get image 
//********************************************************************************** 


//Spawns new enemies up to 10
//gives 150px space between
//They follow waypoints waypoints.js
const enemies = []


function spawnEnemies(spawnCount) {
    for (let i = 1; i < spawnCount + 1; i++) {
        const xOffset = i * 150
        enemies.push(
            new Enemy({
                position: {x: waypoints[0].x - xOffset, y: waypoints[0].y}
            })
        )
    }
}

//********************************************************************************** 
//define round number
let roundNumber = 1;
//define buildings array
const buildings = []
//define enemycount 
let enemyCount = 3
//LIFE COUNT
let hearts = 10
//
const explosions = []
spawnEnemies(enemyCount)
//COINS
let coins = 100
//define active tile 
let activeTile = undefined
//define PAUSE
let animationID = null;
let isPaused = false;
let isGameOver = false;
let gameStarted = false;



const end = waypoints[waypoints.length - 1];
const END_RADIUS = 12;

function reachedEnd(enemy, end) {
  const ex = enemy.center?.x ?? (enemy.position.x + (enemy.width  ? enemy.width  / 2 : 0));
  const ey = enemy.center?.y ?? (enemy.position.y + (enemy.height ? enemy.height / 2 : 0));
  const dx = end.x - ex;
  const dy = end.y - ey;
  return (dx*dx + dy*dy) <= END_RADIUS * END_RADIUS;
}

function animate() {
  // If paused or game over, no next frame.
  if (isPaused || isGameOver) {
    animationID = null; 
    return;
  }

  // Schedule next frame
  animationID = requestAnimationFrame(animate);

  // ---game rendering/update code ---
  c.drawImage(image, 0, 0);

  for (let i = enemies.length - 1; i >= 0; i--) {
    const enemy = enemies[i];
    enemy.update();

    if (reachedEnd(enemy, end)) {
      hearts -= 1;
      enemies.splice(i, 1);
      document.querySelector('#hearts').textContent = hearts;
      if (hearts === 0) {
        isGameOver = true;
        if (animationID != null) {
          cancelAnimationFrame(animationID);
          animationID = null;
        }
        document.querySelector('#gameOver').style.display = 'flex';
        return;
      }
    }
  }

  for (let i = explosions.length - 1; i >= 0; i--) {
    const explosion = explosions[i];
    explosion.draw();
    explosion.update();
    if (explosion.frames.current >= explosion.frames.max - 1) {
      explosions.splice(i, 1);
    }
  }

  if (enemies.length === 0) {
    roundNumber++;
    console.log('Round ' + roundNumber);
    document.getElementById('roundDisplay').textContent = 'Round ' + roundNumber;
    // If round === 5 and enemies.length === 0, you win
    enemyCount += 2;
    spawnEnemies(enemyCount);
  }

  placementTiles.forEach(tile => tile.update(mouse));

  buildings.forEach((building) => {
    building.update();
    building.target = null;
    const validEnemies = enemies.filter(enemy => {
      const xDiff = enemy.center.x - building.center.x;
      const yDiff = enemy.center.y - building.center.y;
      const distance = Math.hypot(xDiff, yDiff);
      return distance < enemy.radius + building.radius;
    });
    building.target = validEnemies[0];

    for (let i = building.projectiles.length - 1; i >= 0; i--) {
      const projectile = building.projectiles[i];

      projectile.update();
      const xDiff = projectile.enemy.center.x - projectile.position.x;
      const yDiff = projectile.enemy.center.y - projectile.position.y;
      const distance = Math.hypot(xDiff, yDiff);

      if (distance < projectile.enemy.radius + projectile.radius) {
        projectile.enemy.health -= 20;
        if (projectile.enemy.health <= 0) {
          const enemyIndex = enemies.findIndex(enemy => projectile.enemy === enemy);
          if (enemyIndex > -1) {
            enemies.splice(enemyIndex, 1);
            coins += 25;
            document.querySelector('#coins').innerHTML = coins;
          }
        }
        explosions.push(new Sprite({
          position: { x: projectile.position.x, y: projectile.position.y },
          imageSrc: '/static/GardenTD/img/explosion.png',
          frames: { max: 4 },
          offset: { x: 0, y: 0 }
        }));
        building.projectiles.splice(i, 1);
      }
    }
  });
}
// -----------------------------------------------
// START BUTTON
const startBtn = document.getElementById('startButton');
startBtn.addEventListener('click', () => {
  if (gameStarted) return;            // prevent double-start
  if (!imageReady) {
    alert('Please wait, map still loading...');
    return;
  }

  gameStarted = true;
  startBtn.style.display = 'none';    // hide start button after clicking
  document.getElementById('pauseButton').style.display = 'inline-block';
  animationID = requestAnimationFrame(animate);
});
// --- Pause/Resume button wiring ---
const pauseBtn = document.getElementById('pauseButton');
pauseBtn.addEventListener('click', () => {
  if (isGameOver) return;
  isPaused = !isPaused;
  pauseBtn.textContent = isPaused ? 'Resume' : 'Pause';
  if (isPaused) {
    stopLoop();
  } else {
    startLoop();
  }
});
//********************************************************************************** 

//define mouse
const mouse = {
    x: undefined,
    y: undefined
}
//********************************************************************************** 
//Watching for clickes on the activeTile. 
//If click, placement tile = occupied
//always occupied, cannot be clicked again

//BUILD A BUILDING
canvas.addEventListener('click', (event) => {
    if (activeTile && !activeTile.isOccupied && coins - 50 >= 0) {
        coins -= 50
        document.querySelector('#coins').innerHTML = coins
        buildings.push(new Building({
            position: {
                x: activeTile.position.x,
                y: activeTile.position.y
            }
            
        })
    )
        activeTile.isOccupied = true
        buildings.sort((a, b) => {
            return a.position.y - b.position.y
        })
    }
})

//Watching for if mouse collides with placement tile
//When mouse is within placement tower border...
//activeTile is set, when no longer, it resets null
window.addEventListener('mousemove', function (event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  mouse.x = (event.clientX - rect.left) * scaleX;
  mouse.y = (event.clientY - rect.top) * scaleY;

  activeTile = null;
  for (let i = 0; i < placementTiles.length; i++) {
    const tile = placementTiles[i];
    if (
      mouse.x > tile.position.x &&
      mouse.x < tile.position.x + tile.size &&
      mouse.y > tile.position.y &&
      mouse.y < tile.position.y + tile.size
    ) {
      activeTile = tile;
      break;
    }
  }
})

//********************************************************************************** 