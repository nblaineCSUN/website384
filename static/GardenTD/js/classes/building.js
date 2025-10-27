class Building extends Sprite {
  constructor({ position = { x: 0, y: 0 } }) {
    super({
      position,
      imageSrc: '/static/GardenTD/img/archertower.png',
      frames: { max: 6 },
      offset: { x: 0, y: -80 },
    });

    this.width = 32;
    this.height = 16;
    this.center = {
      x: this.position.x + this.width / 2,
      y: this.position.y + this.height / 2,
    };
    this.projectiles = [];
    this.radius = 175;
    this.target;

    // cooldown tracking
    this.shootCooldown = 0;    // counts down to next shot
    this.shootInterval = 150;   // number of frames between shots (≈1 second at 60fps)
  }

  update() {
    this.draw();
    if (this.target || (!this.target && this.frames.current !== 0)) super.update();

    if (this.shootCooldown > 0) {
      this.shootCooldown--; // count down each frame
    }

    if (
      this.target &&
      this.frames.current === 5 &&
      this.shootCooldown === 0
    ) {
      this.shoot();
      this.shootCooldown = this.shootInterval; // reset cooldown
    }
  }

  shoot() {
    this.projectiles.push(
      new Projectile({
        position: {
          x: this.center.x - 20,
          y: this.center.y - 110,
        },
        enemy: this.target,
      })
    );
  }
}
