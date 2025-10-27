//Construct Enemy
class Enemy extends Sprite {
    constructor({position = { x: 0, y: 0} }) {
        super({
            position, 
           // imageSrc: './img/orc.png', 
            imageSrc: './static/GardenTD/img/PNG/Slime1/Walk/Slime1_Walk_full.png', 
            frames: { max: 32, columns: 8 }
        })

        this.position = position
        this.width = 64
        this.height = 64
        this.waypointIndex = 0
        this.center = {
            x: this.position.x + this.width / 2,
            y: this.position.y + this.height / 2
        }
        this.radius = 50
        //enemy health
        this.health = 100
        this.velocity = {
            x: 0,
            y: 0
        }

    }
    //draw enemy
    draw() {
        super.draw()
        //Health Bar Reduce
        c.fillStyle = 'red'
        c.fillRect(this.position.x, this.position.y - 15, this.width, 10)

        //Health Bar Full
        c.fillStyle = 'green'
        c.fillRect(this.position.x, this.position.y - 15, this.width * this.health / 100, 10) 
    }

    //updates enemy position and follows waypoint
    update() {
        this.draw()
        super.update()

        const waypoint = waypoints[this.waypointIndex]
        const yDistance = waypoint.y - this.center.y
        const xDistance = waypoint.x - this.center.x
        const angle = Math.atan2(yDistance, xDistance)

        //velocity
        const speed = 1.0

        this.velocity.x = Math.cos(angle) * speed
        this.velocity.y = Math.sin(angle) * speed

        this.position.x += this.velocity.x
        this.position.y += this.velocity.y 
        this.center = {
            x: this.position.x + this.width / 2,
            y: this.position.y + this.height / 2
        }

        if (
            Math.abs(Math.round(this.center.x) - Math.round(waypoint.x)) < 
                Math.abs(this.velocity.x) && 
            Math.abs(Math.round(this.center.y) - Math.round(waypoint.y)) <
                Math.abs(this.velocity.y) &&
            this.waypointIndex < waypoints.length -1 
        ) {
            this.waypointIndex++
        }
    }
}