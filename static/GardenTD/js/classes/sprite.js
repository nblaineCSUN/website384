class Sprite {
  constructor({ position = { x: 0, y: 0 }, imageSrc, frames = { max: 1 }, offset = { x: 0, y: 0 } }) {
    this.position = position
    this.image = new Image()
    this.image.src = imageSrc
    this.frames = {
      max: frames.max,
      current: 0,
      elapsed: 0,
      hold: frames.hold ?? 7,
      columns: frames.columns ?? frames.max // <-- NEW
    }
    this.offset = offset
  }

  draw() {
    const cols = this.frames.columns
    const frameWidth  = this.image.width / cols
    const rows        = Math.ceil(this.frames.max / cols)
    const frameHeight = this.image.height / rows

    const i  = this.frames.current
    const sx = (i % cols) * frameWidth
    const sy = Math.floor(i / cols) * frameHeight

    c.drawImage(
      this.image,
      sx, sy, frameWidth, frameHeight,
      this.position.x + this.offset.x,
      this.position.y + this.offset.y,
      frameWidth, frameHeight
    )
  }

  update() {
    this.frames.elapsed++
    if (this.frames.elapsed % this.frames.hold === 0) {
      this.frames.current = (this.frames.current + 1) % this.frames.max
    }
  }
}
