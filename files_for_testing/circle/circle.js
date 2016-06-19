function Circle (radius) { //  class
   this.radius= radius; // attribute
   this.getArea= function () { // method
     return (3.14 * this.radius * this.radius);
   }
 }

 var myCircle = new Circle (10); // Circle instance

 function Circle2D (x, y) { // class Circle2D
   this.x = x;
   this.y= y;
 }

// Circle2D is a subclass of Circle
Circle2D.prototype = new Circle(10);

// Circle2D extends Circle with new methods
Circle2D.prototype.getX = function () {
  return (x);
}
Circle2D.prototype.getY = function () {
  return (y);
}
