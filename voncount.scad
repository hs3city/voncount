BASE_THICKNESS = 1;
PIMB_L = 84.5;
PIMB_W = 56.0;
PIMB_H = 1.45;
PIMB_X = 0;
PIMB_Y = -30;
PIMB_Z = 0;
PIMB_R = 3;
PIMB_SCREWS_Y = [-PIMB_W / 2 + 4, PIMB_W / 2 - 4];
PIMB_SCREWS_X = [-PIMB_L / 2 + 23, PIMB_L / 2 - 4];
PIMB_SCREWS_M = 3;
PIMB_SCREWS_LENGTH = BASE_THICKNESS * 5; // from outside of base
PIMB_NUT_HEIGHT = 1;
DIGIT_L = 18;
DIGIT_W = 25;
DIGIT_X = 0;
DIGIT_Y = 60;
DIGIT_SPACE = .3;
CAMERA_R = 7;
CAMERA_SPACE = .3;
CAMERA_X = 0;
CAMERA_Y = 20;
CAMERA_SCREWS_X = [21 / 2, -21 / 2];
CAMERA_SCREWS_Y = [13.5 / 2, -13.5 / 2];
CAMERA_SCREWS_LENGTH = 14.5; // from outside of base
CAMERA_NUT_HEIGHT = 1;
CAMERA_SCREWS_M = 2;

$fn=20;
module MB() {
    translate([PIMB_X, PIMB_Y, PIMB_Z]) {
            linear_extrude(PIMB_H) {
                difference () {
                    minkowski() {
                        square([PIMB_L-2 * PIMB_R, PIMB_W - 2 * PIMB_R], center=true);
                        circle(PIMB_R);
                    }
                    for(x=PIMB_SCREWS_X, y=PIMB_SCREWS_Y) {
                        translate([x, y, 0]) {
                            circle(PIMB_SCREWS_M / 2);
                        }
                    }
                }
            }
    }
}

module digit_cutout() {
    translate([DIGIT_X, DIGIT_Y, 0]) {
        cube([DIGIT_L + 2 * DIGIT_SPACE, DIGIT_W + 2 * DIGIT_SPACE, 3 * BASE_THICKNESS], center=true);
    }
}

module camera_cutout() {
    translate([CAMERA_X, CAMERA_Y, 0]) {
        cylinder(r=CAMERA_R + CAMERA_SPACE, h=3 * BASE_THICKNESS, center=true);
    }
}
module camera_screws() {
    translate([CAMERA_X, CAMERA_Y, 0]) {
        for(x=CAMERA_SCREWS_X, y=CAMERA_SCREWS_Y) {
            translate([x, y, 0]) {
                difference() {
                    cylinder(r=CAMERA_SCREWS_M * 1.1 + 1, h=CAMERA_SCREWS_LENGTH);
                    translate([0, 0, BASE_THICKNESS]) cylinder(r=CAMERA_SCREWS_M / 2, h=CAMERA_SCREWS_LENGTH);
                    translate([0, 0, CAMERA_SCREWS_LENGTH - 3 * CAMERA_NUT_HEIGHT]) cylinder(r=CAMERA_SCREWS_M * 1.1 , h=CAMERA_SCREWS_LENGTH, $fn=6);
                }
            }
        }
    }

}


module pimb_screws() {
    translate([PIMB_X, PIMB_Y, 0]) {
        for(x=PIMB_SCREWS_X, y=PIMB_SCREWS_Y) {
            translate([x, y, 0]) {
                difference() {
                    cylinder(r=PIMB_SCREWS_M * 1.1 + 1, h=PIMB_SCREWS_LENGTH);
                    translate([0, 0, BASE_THICKNESS]) cylinder(r=PIMB_SCREWS_M / 2, h=PIMB_SCREWS_LENGTH);
                    translate([0, 0, PIMB_SCREWS_LENGTH - 3 * PIMB_NUT_HEIGHT]) cylinder(r=PIMB_SCREWS_M * 1.1 , h=PIMB_SCREWS_LENGTH, $fn=6);
                }
            }
        }
    }
}

module base() {
    difference() {
        translate([0, 0, BASE_THICKNESS / 2]) {
            cube([400, 200, BASE_THICKNESS], center=true);
        }
        translate([0, -20, -BASE_THICKNESS]) linear_extrude(BASE_THICKNESS * 1.5) voncount();
        digit_cutout();
        camera_cutout();
    }
    camera_screws();
    pimb_screws();
}


module voncount() {
    rotate(180) scale(.3) import(file="voncount.svg", center=true);
}
/*
module hex_grid() {
    CELL_SIZE = 10;
    CELL_WALL_SIZE = 1;
    CELL_SPACE_Y = (CELL_SIZE *sqrt(3) / 2 + CELL_WALL_SIZE) / 2;
    CELL_SPACE_X = CELL_SPACE_Y * sqrt(3) * 2;
    GRID_HEIGHT = 2;
    for (x=[-1:1], y=[-6:6]) {
        x = x + (abs(y) % 2 - .5) / 2;
        translate([x * CELL_SPACE_X, y * CELL_SPACE_Y, 0]) {
            difference() {
                cylinder(r=CELL_SIZE / 2 + CELL_WALL_SIZE * sqrt(3), h=GRID_HEIGHT, $fn=6);
                translate([0, 0, -1]) cylinder(r=CELL_SIZE / 2, h=GRID_HEIGHT + 2, $fn=6);
            }
        }
    }
}
*/

module rotated_front() {
    translate([0, 0, -210]) {
        rotate(25, [0, 0, 1]) {
            rotate(-75, [1, 0, 0]) {
                translate([30, -150, -10]) {
                    union() {
                        translate([0, 0, BASE_THICKNESS * 3]) MB();
                        base();
                    }
                }
            }
        }
    }
}
module rotated_walls() {
    translate([-30, 150, 10]) {
        rotate(75, [1, 0, 0]) {
            rotate(-25, [0, 0, 1]) {
                translate([0, 0, 210]) {
                    translate([0, 0, 500]) cube(1000, center=true);
                    rotate(-90, [1, 0, 0]) translate([0, 0, 500]) cube(1000, center=true);
                    rotate(-90, [0, 1, 0]) translate([0, 0, 500]) cube(1000, center=true);
                }
            }
        }
    }
}

module corner_box() {
    difference() {
        union() {
            translate([0, 0, BASE_THICKNESS * .5]) MB();
            base();
        }
        rotated_walls();
    }
}

module down(z) {
    up(-z) children();
}

module up(z) {
    translate([0, 0, z]) children();
}

module spacers_15mm() {
    for (x=[-1, 1], y=[-1, 1]) {
        translate([x * 5, y * 5, 0]) {
            difference() {
                cylinder(r=3, h=15, $fn=6);
                down(1) cylinder(r=1.3, h=17);
            }
        }
    }
}
