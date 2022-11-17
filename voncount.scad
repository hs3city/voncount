BASE_THICKNESS = 1;
PIMB_L = 85;
PIMB_W = 56.0;
PIMB_H = 1.45;
PIMB_R = 3;
PIMB_MARGINS = 3;
PIMB_SCREWS_POS = [
    [-PIMB_L / 2 + 22.5, -PIMB_W/2 + 3.5, [180]],
    [PIMB_L / 2 - 3.5, -PIMB_W/2 + 3.5, [180, 225, 270]],
    [-PIMB_L / 2 + 22.5, PIMB_W/2 - 3.5, [0]],
    [PIMB_L / 2 - 3.5, PIMB_W/2 - 3.5, [0, 315, 270]],
];
PIMB_CONNECTOR_HOLE = [
    [PIMB_L / 2 - 10.6, PIMB_W / 2, 10, 7],
    [-PIMB_L / 2, PIMB_W / 2 - 10.25, 16, 6],
];
PIMB_SCREWS_M = 2.5;
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

BOX_BOTTOM = 1;
BOX_WALLS = 1;
BOX_RIDGE = 2;
PIMB_UNDER_BOARD_SPACE = 3; // space for sunken screw heads
PIMB_SCREW_PADS_R = 3.5; // actually they're more like 3, but there is some extra space
PIMB_SCREW_HEAD_R = 2.7;
SCREW_HOLE_FACTOR = 1.2; // if screw is M2, make size of hole this much larger

MAGNET_R = 7.5;
MAGNET_H = 2.2;
BOX_ROTATION_FROM_VERTICAL = 15;

$fn=20;
function enforce_3_vector(x) = is_list(x) ? x : [x, x, x];

module rounded_corner_cube(dimensions, r=0) {
    dimensions = enforce_3_vector(dimensions);
    r = enforce_3_vector(r);
    up(dimensions.z / 2) {
        minkowski() {
            cube(dimensions - 2 * r, center=true);
            scale(r) sphere(r=1);
        }
    }
}

module MB_no_holes () {
    linear_extrude(PIMB_H) {
        minkowski() {
            square([PIMB_L-2 * PIMB_R, PIMB_W - 2 * PIMB_R], center=true);
            circle(PIMB_R);
        }
    }
}
module MB() {
    difference() {
        MB_no_holes();
        repeat_for_MB_screw_positions() {
            down(1) cylinder(r=PIMB_SCREWS_M / 2, h=PIMB_H + 2);
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
    repeat_for_MB_screw_positions() {
        difference() {
            cylinder(r=PIMB_SCREWS_M * 1.1 + 1, h=PIMB_SCREWS_LENGTH);
            translate([0, 0, BASE_THICKNESS]) cylinder(r=PIMB_SCREWS_M / 2, h=PIMB_SCREWS_LENGTH);
            translate([0, 0, PIMB_SCREWS_LENGTH - 3 * PIMB_NUT_HEIGHT]) cylinder(r=PIMB_SCREWS_M * 1.1 , h=PIMB_SCREWS_LENGTH, $fn=6);
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
    scale(.1) import(file="voncount.svg", center=true);
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

module repeat_for_MB_screw_positions() {
    for(x_y_rots=PIMB_SCREWS_POS) {
        x = x_y_rots[0];
        y = x_y_rots[1];
        for (rot=x_y_rots[2]) {
            translate([x, y, 0]) rotate([0, 0, rot]) children();
        }
    }
}

module make_MB_base_holes_and_support() {
    difference() {
        union() {
            children();
            repeat_for_MB_screw_positions() {
                translate([-PIMB_SCREW_PADS_R, 0, 0]) cube([PIMB_SCREW_PADS_R * 2, PIMB_SCREW_PADS_R * 2 + 10, BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE]);
                cylinder(r=PIMB_SCREW_PADS_R, h=BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE);
            }
        }
        repeat_for_MB_screw_positions() {
            down(BOX_BOTTOM) cylinder(r=PIMB_SCREW_HEAD_R, h=BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE);
            cylinder(r=PIMB_SCREWS_M / 2 * SCREW_HOLE_FACTOR, h=BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE + 1);
        }
    }
}

module cut_out_connector_holes() {
    difference() {
        children();
        for (x_y_w_h = PIMB_CONNECTOR_HOLE) {
            let (x = x_y_w_h[0], y=x_y_w_h[1], w=x_y_w_h[2], h=x_y_w_h[3]) {
                translate([x, y, BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE]) rounded_corner_cube([w, w, h], r=.5);
            }
        }
    }
}

module cut_out_text() {
    difference() {
        children();
        linear_extrude(BOX_BOTTOM / 4) {
            scale([-1, 1, 1]) voncount();
            scale([-.7, .7, 1]) {
                translate([0, 18, 0]) text("Count von Count", halign="center");
                translate([0, -27, 0]) text("HS3.pl", halign="center");
            }
        }
    }
}

module BOX(offset, h=10, z_r=1) rounded_corner_cube([PIMB_L + 2 * offset + PIMB_MARGINS * 2, PIMB_W + 2 * offset + PIMB_MARGINS * 2, h ], [4 + offset, 4 + offset, z_r]);
module OUTER_BOX() BOX(BOX_WALLS);
module INNER_BOX() up(BOX_WALLS) BOX(0);

module pibox_holder() {
    render() {
        intersection() {
            up(500) cube(1000, center=true);  // only z > 0
            let (pad_size = (MAGNET_R + BOX_WALLS) * 2) {
                difference() {
                    union() {
                        translate([(PIMB_L / 2 + BOX_WALLS + PIMB_MARGINS), 0 , 0]) {
                            render() cut_out_connector_holes() translate([-PIMB_L / 2 - PIMB_MARGINS - BOX_WALLS + .45, 7, 0]) holder(110, 1);
                        }
                        magnet_holder_no_hole(-(53 - pad_size / 2), 30, pad_size);
                        magnet_holder_no_hole(57 + pad_size / 2, -60, pad_size);
                    }
                    magnet_holder_hole(-(53 - pad_size / 2), 30, pad_size);
                    magnet_holder_hole(57 + pad_size / 2, -60, pad_size);
                }
            }
        }
    }
}

module magnet_holder_no_hole(pos, rot, pad_size) {
    rotate(-BOX_ROTATION_FROM_VERTICAL, [0, 1, 0]) {
        translate([0, pos, 1.2]) up(pad_size / 2 + 1) rotate(rot, [1, 0, 0]) rotate(90, [0, 1, 0]) {
            rounded_corner_cube([pad_size,  pad_size, 1.5 * BOX_WALLS + MAGNET_H], [2, 2, 0]);
        }
    }
}
module magnet_holder_hole(pos, rot, pad_size) {
    rotate(-BOX_ROTATION_FROM_VERTICAL, [0, 1, 0]) {
        translate([0, pos, 1.2]) up(pad_size / 2 + 1) rotate(rot, [1, 0, 0]) rotate(90, [0, 1, 0]) {
            up(BOX_WALLS / 2) cylinder(r=MAGNET_R, h=MAGNET_H);
            up(BOX_WALLS) translate([-(pad_size + MAGNET_R / 4), 0, 0]) rounded_corner_cube([2 * pad_size, MAGNET_R * 2, 1.5 * BOX_WALLS + MAGNET_H], 0);
        }
    }
}

module pibox_bottom() {
    translate([(PIMB_L / 2 + BOX_WALLS + PIMB_MARGINS), 0 , 0])
        intersection() {
            OUTER_BOX();
            cut_out_text() cut_out_connector_holes() make_MB_base_holes_and_support() {
                difference() {
                    OUTER_BOX();
                    union() {
                        up(BOX_BOTTOM + PIMB_UNDER_BOARD_SPACE + PIMB_H) difference() {
                            up(100) cube(200, center=true);
                            down(1) BOX(BOX_WALLS / 2, h = BOX_RIDGE + 1, z_r=0);
                        }
                        INNER_BOX();
                        // up(BOX_BOTTOM*3) scale([1, 1, 10]) MB_no_holes();
                    }
                }
            }
        }
}

pibox_bottom();
pibox_holder();

module holder(h, thickness = 0.5) {
    rotate(90, [1, 0, 0]) {
        translate([thickness / 2, thickness / 2, -h/2]) {
            linear_extrude(h) {
                minkowski() {
                    union() {
                        translate([-.005, -.005]) square([10, .01]);
                        rotate(90) polygon([[0, .5], [7.7, 2.57], [4, .5]]);
                    }
                    circle(r=thickness/2 - 0.001);
                }
            }
        }
    }
}
