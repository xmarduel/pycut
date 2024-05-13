"""
generate a svg file for a gear with given diameter and nb of teeth

for hobbymat: i think, the modul of the gears is "1"

nb teeth is 30 / 35 / 40 / 50 / 55 / 60 / 65 / 70 / 75 

the ratio between a tooth "base" and an empty space is undefined...
I will take 2 to 1, seems optically good...
"""

import argparse
import math

from typing import Dict
from typing import Any

SVG_2_GEARS_ANIMATED_TPL = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="400mm"
   height="400mm"
   viewBox="0 0 400 400"
   version="1.1"
   id="gear_hobbymat">
   <defs>
     %(GEAR)s
     %(REINFORCMENT)s
     %(BEARING)s
   </defs>

   <!--
   module                   : %(GEAR_MODULE)f
   nb-teeth                 : %(GEAR_NB_TEETH)d
   ratio-teeth-gap          : %(GEAR_RATIO_GAP_TEETH)f
   teeth-curvature          : %(GEAR_TEETH_CURVATURE)f
   ratio-teeth-head-base    : %(GEAR_TEETH_RATION_HEAD_BASE)f
   -->

   <g>
     <!-- first gear -->
     <use href="#gear"    id="gear_1"    transform="translate(200,200) rotate(0)" >
      <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="0 0 0" to="380 0 0" dur="%(ANIMATE_PERIOD)fs" additive="sum" repeatCount="indefinite" />
     </use>
     <use href="#bearing" id="bearing_1" transform="translate(200,200)">
      <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="0 0 0" to="380 0 0" dur="%(ANIMATE_PERIOD)fs" additive="sum" repeatCount="indefinite" />
     </use>

     <!-- second gear -->
     <use href="#gear"    id="gear_2"    transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(0)">
      <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="%(SECOND_GEAR_ROTATION_ANIM_START)f 0 0" to="%(SECOND_GEAR_ROTATION_ANIM_END)f 0 0" dur="%(ANIMATE_PERIOD)fs" additive="sum" repeatCount="indefinite" />
    </use>
     
     <use href="#bearing" id="bearing_2" transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(0)">
       <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="%(SECOND_GEAR_ROTATION_ANIM_START)f 0 0" to="%(SECOND_GEAR_ROTATION_ANIM_END)f 0 0" dur="%(ANIMATE_PERIOD)fs" additive="sum" repeatCount="indefinite" />
     </use>

     <!-- reference lines -->
     
     <!-- gear1 horizontal axis -->
     <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M 0 200 L 300 200" ></path>
     <!-- gear1 vertical axis -->
     <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M 200 0 L 200 300" ></path>
    
     <!-- middle vertical -->
     <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M %(SECOND_GEAR_X_LEFT)f 0 L %(SECOND_GEAR_X_LEFT)f 300" ></path>

     <!-- gear2 vertical axis -->     
     <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M %(SECOND_GEAR_X_POS)f 0 L %(SECOND_GEAR_X_POS)f 300" ></path>

   </g>
   
</svg>
"""

SVG_2_GEARS_STATIC_TPL = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="400mm"
   height="400mm"
   viewBox="0 0 400 400"
   version="1.1"
   id="gear_hobbymat">
   <defs>
     %(GEAR)s
     %(REINFORCMENT)s
     %(BEARING)s
   </defs>

   <!--
   module                   : %(GEAR_MODULE)f
   nb-teeth                 : %(GEAR_NB_TEETH)d
   ratio-teeth-gap          : %(GEAR_RATIO_GAP_TEETH)f
   teeth-curvature          : %(GEAR_TEETH_CURVATURE)f
   ratio-teeth-head-base    : %(GEAR_TEETH_RATION_HEAD_BASE)f
   -->

   <g>
     <!-- first gear -->
     <use href="#gear"    id="gear_1"    transform="translate(200,200) rotate(0)"></use>
     <use href="#bearing" id="bearing_1" transform="translate(200,200) rotate(0)"></use>

     <!-- second gear -->
     <use href="#gear"    id="gear_2"    transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(%(SECOND_GEAR_ROTATION_ANIM_START)f)"></use>
     <use href="#bearing" id="bearing_2" transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(%(SECOND_GEAR_ROTATION_ANIM_START)f)"> </use>

     <!-- reference lines -->
    <!-- gear1 horizontal axis -->
    <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M 0 200 L 300 200" ></path>
    <!-- gear2 vertical axis -->
    <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M 200 0 L 200 300" ></path>
    
    <!-- middle verical -->
    <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M %(SECOND_GEAR_X_LEFT)f 0 L %(SECOND_GEAR_X_LEFT)f 300" ></path>

    <!-- gear2 horizontal axis -->
    <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M -300 0 L 300 0" 
      transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(%(SECOND_GEAR_ROTATION_ANIM_START)f)"></path>
    <!-- gear2 vertical axis -->
    <path style="fill:#ffcccc;stroke:#000000;stroke-width:0.050000" d="M 0.000000 -300 L 0.000000 300" 
      transform="translate(%(SECOND_GEAR_X_POS)f,200) rotate(%(SECOND_GEAR_ROTATION_ANIM_START)f)"></path>
    

   </g>
   
</svg>
"""


class GearMaker:
    """ """

    CENTER = (0, 0)  # mm

    # definition of modul
    # MODULE = PITCH_CIRCLE_DIAMETER / NB_TEETHS
    MODULE = 1.0

    # Gear basic size # change me
    NB_TEETHS = 60

    # size of the gear
    PITCH_CIRCLE_DIAMETER = MODULE * NB_TEETHS
    PITCH_CIRCLE_RADIUS = PITCH_CIRCLE_DIAMETER / 2.0

    # Zähne
    FOOT_HEIGHT = MODULE * 1.25
    HEAD_HEIGHT = MODULE

    # other radius
    FOOT_CIRCLE_RADIUS = (
        PITCH_CIRCLE_RADIUS - FOOT_HEIGHT
    )  # ( NB_TEETHS - 2.5 ) * MODULE / 2.0 # smaller than the PITCH_CICLE_RADIUS
    HEAD_CIRCLE_RADIUS = (
        PITCH_CIRCLE_RADIUS + HEAD_HEIGHT
    )  # ( NB_TEETHS + 2.0 ) * MODULE / 2.0 # larger than the PITCH_CICLE_RADIUS

    # pitch
    PITCH = (
        MODULE * math.pi
    )  # länge des bogen zwischen 2 Zähne auf den PITCH_CIRCLE : (2pi * R) / z

    # TEETH CURVATURE
    TEETH_CURVATURE = 9.0 / 4.0 * (FOOT_HEIGHT + HEAD_HEIGHT)  # about 5
    # you can adjust it to change the look of the teeth... big value -> straight lines , small value -> round

    # ratio gear gap/teeth
    RATIO_TEETH_GAP_BASE = 0.6  # teeth base about 2 times longer than the gap
    RATIO_TEETH_HEAD_BASE = 0.4  # teeth base about 2 times longer than the head

    BEARING_RADIUS = 10  # mm
    BEARING_NUT_LENGTH = 4  # mm
    BEARING_NUT_HEIGHT = 2  # mm

    REINFORCMENT_RADIUS = 15  # mm

    # SVG VIEW
    STROKE_WIDTH = 0.025
    STROKE_COLOR = "#000000"
    GEAR_COLOR = "#cccccc"
    BEARING_COLOR = "#ffcccc"

    def __init__(self):
        """ """
        print(" generating gear for %d teeth" % GearMaker.NB_TEETHS)

        print("NB_TEETHS             : %d" % GearMaker.NB_TEETHS)
        print("MODULE                : %d" % GearMaker.MODULE)
        print("PITCH_CIRCLE_DIAMETER : %4.2f" % GearMaker.PITCH_CIRCLE_DIAMETER)
        print("PITCH_CIRCLE_RADIUS   : %4.2f" % GearMaker.PITCH_CIRCLE_RADIUS)
        print("FOOT_HEIGHT           : %4.2f" % GearMaker.FOOT_HEIGHT)
        print("HEAD_HEIGHT           : %4.2f" % GearMaker.HEAD_HEIGHT)
        print("FOOT_CIRCLE_RADIUS    : %4.2f" % GearMaker.FOOT_CIRCLE_RADIUS)
        print("HEAD_CIRCLE_RADIUS    : %4.2f" % GearMaker.HEAD_CIRCLE_RADIUS)
        print(
            "PITCH                 : %4.2f [length of the arc of the pitch circle between 2 teeths]"
            % GearMaker.PITCH
        )
        print(
            "-> ALPHA FREQ (rad)   : %4.2f"
            % (GearMaker.PITCH / GearMaker.PITCH_CIRCLE_RADIUS)
        )
        print(
            "-> ALPHA FREQ (deg)   : %4.2f"
            % ((GearMaker.PITCH / GearMaker.PITCH_CIRCLE_RADIUS) * 180 / math.pi)
        )

        print(
            "coeff  pitch circle diameter / foot circle diameter    : %f"
            % (self.PITCH_CIRCLE_RADIUS / self.FOOT_CIRCLE_RADIUS)
        )
        print(
            "coeff  head  circle diameter / pitch circle diameter   : %f"
            % (self.HEAD_CIRCLE_RADIUS / self.PITCH_CIRCLE_RADIUS)
        )

        self.gear_segments = []
        self.bearing_segments = []

        self._start_pt = [0, 0]
        self._curr_pt = [0, 0]
        self._end_pt = [0, 0]

    @classmethod
    def setup(cls):
        """ """
        # size of the gear
        cls.PITCH_CIRCLE_DIAMETER = cls.MODULE * cls.NB_TEETHS
        cls.PITCH_CIRCLE_RADIUS = cls.PITCH_CIRCLE_DIAMETER / 2.0

        # Zähne
        cls.FOOT_HEIGHT = cls.MODULE * 1.25
        cls.HEAD_HEIGHT = cls.MODULE

        # other radius
        cls.FOOT_CIRCLE_RADIUS = (
            cls.PITCH_CIRCLE_RADIUS - cls.FOOT_HEIGHT
        )  # ( NB_TEETHS - 2.5 ) * MODULE / 2.0 # smaller than the PITCH_CICLE_RADIUS
        cls.HEAD_CIRCLE_RADIUS = (
            cls.PITCH_CIRCLE_RADIUS + cls.HEAD_HEIGHT
        )  # ( NB_TEETHS + 2.0 ) * MODULE / 2.0 # larger than the PITCH_CICLE_RADIUS

        # pitch
        cls.PITCH = (
            cls.MODULE * math.pi
        )  # länge des bogen zwischen 2 Zähne auf den PITCH_CIRCLE : (2pi * R) / z

    def rotate(self, pt, angle):
        """ """
        mat = [[math.cos(angle), math.sin(-angle)], [math.sin(angle), math.cos(angle)]]

        return (
            mat[0][0] * pt[0] + mat[0][1] * pt[1],
            mat[1][0] * pt[0] + mat[1][1] * pt[1],
        )

    def translate(self, pt, coeff):
        """ """
        mat = [[coeff, 0.0], [0.0, coeff]]

        return (
            mat[0][0] * pt[0] + mat[0][1] * pt[1],
            mat[1][0] * pt[0] + mat[1][1] * pt[1],
        )

    def get_gear(self) -> str:
        """ """
        self.make_gear()

        gear_path = " ".join(self.gear_segments)

        path = """
            <path id="gear" style="fill:%s;stroke:%s;stroke-width:%f"
                d=" %s z"
            />
        """ % (
            self.GEAR_COLOR,
            self.STROKE_COLOR,
            self.STROKE_WIDTH,
            gear_path,
        )

        return path

    def get_bearing(self) -> str:
        """ """
        self.make_bearing()

        bearing_path = " ".join(self.bearing_segments)

        path = """
        <path id="bearing" style="fill:%s;stroke:%s;stroke-width:%f"
            d="M %s"
        />
        """ % (
            self.BEARING_COLOR,
            self.STROKE_COLOR,
            self.STROKE_WIDTH,
            bearing_path,
        )

        return path

    def get_reinforcement(self) -> str:
        """ """
        path = """
        <circle id="reinforcement" style="fill:%s;stroke:%s;stroke-width:%f"
            cx="0" cy="0" r="%s"
        />
        """ % (
            self.GEAR_COLOR,
            self.STROKE_COLOR,
            self.STROKE_WIDTH,
            self.REINFORCMENT_RADIUS,
        )

        if self.FOOT_CIRCLE_RADIUS > self.REINFORCMENT_RADIUS:
            return path

        return ""

    def make_gear(self):
        """ """
        self._start_pt = (self.FOOT_CIRCLE_RADIUS, 0.0)

        initial_move = """ M  %(start_x)s %(start_y)s      
        """ % {
            "start_x": self._start_pt[0],
            "start_y": self._start_pt[1],
        }

        self.gear_segments.append(initial_move)

        for _ in range(self.NB_TEETHS):
            self._make_teeth()

    def _make_teeth(self):
        """
        exact teeth

        alpha = alpha_gap + alpha_base  [base + gap]

        alpha_gap = r * alpha_base

        => alpha_base = alpha * ( 1 / (1+r) )
        => alpha_gap  = alpha * ( r / (1+r) )
        """
        start_pt = self._start_pt

        alpha = self.PITCH / self.PITCH_CIRCLE_RADIUS

        alpha_gap = alpha * self.RATIO_TEETH_GAP_BASE / (1 + self.RATIO_TEETH_GAP_BASE)
        alpha_teeth = alpha * 1.0 / (1 + self.RATIO_TEETH_GAP_BASE)

        gap_pt = self.rotate(start_pt, alpha_gap)

        rotation = 0
        arc_path = 0  # small arc
        clockwise = 1

        # 1- first an arc along the base for the teeth "gap"
        arc = """ A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(gap_x)s %(gap_y)s
        """ % {
            "radius": self.FOOT_CIRCLE_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "gap_x": gap_pt[0],
            "gap_y": gap_pt[1],
        }

        self.gear_segments.append(arc)

        """
        ATTENTION!
        
        we give 
        
        L_h / L_b = self.RATIO_TEETH_HEAD_BASE = R_L  (ratio of lengths)
        -> the head length is smaller than the base length

        What must be the ratio ALPHA_h / ALPHA_b (ratio of angles) so that
        the ratio of length is satisfied ? Indeed, we are not on the same circle!

        Denoting the diff of height of the base circle and head circle 
        DELTA_H = HEAD_HEIGHT + FOOT_HEIGHT
                                          
        => 
                                                                                                                                              R_h - R_b
        ALPHA_h / ALPHA_b = R_A = R_L / ( 1 + DELTA_H / R )

        """
        DELTA_H = self.HEAD_HEIGHT + self.FOOT_HEIGHT

        RATIO_ANGLE = self.RATIO_TEETH_HEAD_BASE / (
            1.0 + (DELTA_H) / self.PITCH_CIRCLE_RADIUS
        )

        alpha_teeth_head = alpha_teeth * RATIO_ANGLE
        alpha_base_to_head = (alpha_teeth - alpha_teeth_head) / 2.0

        alpha_teeth_cc = alpha_teeth - 2 * alpha_base_to_head

        # now the teeth itself -  arc to the head
        arc_start = gap_pt
        arc_end = self.rotate(arc_start, alpha_base_to_head)

        arc_end = self.translate(
            arc_end, self.HEAD_CIRCLE_RADIUS / self.FOOT_CIRCLE_RADIUS
        )

        arc = """ A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(arc_end_x)s %(arc_end_y)s
        """ % {
            "radius": self.TEETH_CURVATURE,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "arc_end_x": arc_end[0],
            "arc_end_y": arc_end[1],
        }

        self.gear_segments.append(arc)

        # teeth HEAD - you could make an arc
        teeth_HEAD = self.rotate(arc_end, alpha_teeth_cc)

        teeth = """ L %(teeth_x)s %(teeth_y)s 
        """ % {
            "teeth_x": teeth_HEAD[0],
            "teeth_y": teeth_HEAD[1],
        }

        self.gear_segments.append(teeth)

        # arc to the base
        arc_start = teeth_HEAD
        arc_end = self.rotate(arc_start, alpha_base_to_head)
        arc_end = self.translate(
            arc_end, self.FOOT_CIRCLE_RADIUS / self.HEAD_CIRCLE_RADIUS
        )

        # back to the base : arc to the base
        arc = """ A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(arc_end_x)s %(arc_end_y)s
        
        """ % {
            "radius": self.TEETH_CURVATURE,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "arc_end_x": arc_end[0],
            "arc_end_y": arc_end[1],
        }

        self.gear_segments.append(arc)

        self._start_pt = arc_end

    def make_bearing(self):
        """ """
        alpha1 = math.pi / 2 - math.atan(
            (self.BEARING_NUT_LENGTH / 2.0) / self.BEARING_RADIUS
        )
        alpha2 = math.pi / 2 + math.atan(
            (self.BEARING_NUT_LENGTH / 2.0) / self.BEARING_RADIUS
        )

        pt = (self.BEARING_RADIUS, 0)
        pt_A = self.rotate(pt, alpha1)
        pt_B = self.rotate(pt, alpha2)

        arc = """%(start_pt_x)s %(start_pt_y)s A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(end_pt_x)s %(end_pt_y)s
            """ % {
            "start_pt_x": pt_A[0],
            "start_pt_y": pt_A[1],
            "end_pt_x": pt_B[0],
            "end_pt_y": pt_B[1],
            "radius": self.BEARING_RADIUS,
            "rotation": 0,
            "arc_path": 1,
            "clockwise": 0,
        }

        self.bearing_segments.append(arc)

        nut = """ L %(x1)s %(y1)s  %(x2)s %(y2)s  %(x3)s %(y3)s""" % {
            "x1": pt_B[0],
            "y1": pt_B[1] + self.BEARING_NUT_HEIGHT,
            "x2": pt_A[0],
            "y2": pt_B[1] + self.BEARING_NUT_HEIGHT,
            "x3": pt_A[0],
            "y3": pt_A[1],
        }

        self.bearing_segments.append(nut)

    def get_second_gear_rotation(self):
        """ """
        alpha = self.PITCH / self.PITCH_CIRCLE_RADIUS
        alpha_gap = alpha * self.RATIO_TEETH_GAP_BASE / (1 + self.RATIO_TEETH_GAP_BASE)
        alpha_teeth = alpha * 1.0 / (1 + self.RATIO_TEETH_GAP_BASE)

        return (alpha_teeth - alpha_gap) / 2.0 * (180 / math.pi)

    def get_second_gear_x_pos(self):
        """ """
        return self.PITCH_CIRCLE_DIAMETER + 200

    def get_second_gear_x_left(self):
        """ """
        return self.PITCH_CIRCLE_DIAMETER / 2.0 + 200

    @classmethod
    def set_params(cls, params: Dict[str, Any]):
        """ """
        cls.MODULE = 1.0

        # Gear basic size # change me
        cls.NB_TEETHS = params["NB_TEETHS"]

        # size of the gear
        cls.PITCH_CIRCLE_DIAMETER = cls.MODULE * cls.NB_TEETHS
        cls.PITCH_CIRCLE_RADIUS = cls.PITCH_CIRCLE_DIAMETER / 2.0

        # Zähne
        cls.FOOT_HEIGHT = cls.MODULE * params["FOOT_HEIGHT"]
        cls.HEAD_HEIGHT = cls.MODULE * params["HEAD_HEIGHT"]

        # other radius
        cls.FOOT_CIRCLE_RADIUS = (
            cls.PITCH_CIRCLE_RADIUS - cls.FOOT_HEIGHT
        )  # ( NB_TEETHS - 2.5 ) * MODULE / 2.0 # smaller than the PITCH_CICLE_RADIUS
        cls.HEAD_CIRCLE_RADIUS = (
            cls.PITCH_CIRCLE_RADIUS + cls.HEAD_HEIGHT
        )  # ( NB_TEETHS + 2.0 ) * MODULE / 2.0 # larger than the PITCH_CICLE_RADIUS

        # pitch
        cls.PITCH = (
            cls.MODULE * math.pi
        )  # länge des bogen zwischen 2 Zähne auf den PITCH_CIRCLE : (2pi * R) / z

        # TEETH CURVATURE
        cls.TEETH_CURVATURE = params["TEETH_CURVATURE"]
        # you can adjust it to change the look of the teeth... big value -> straight lines , small value -> round

        # ratio gear gap/teeth
        cls.RATIO_TEETH_GAP_BASE = params["RATIO_TEETH_GAP_BASE"]  # ratio = L_gap / L_b
        cls.RATIO_TEETH_HEAD_BASE = params["RATIO_TEETH_HEAD_BASE"]  # ratio = L_h / L_b

        cls.REINFORCMENT_RADIUS = params["REINFORCMENT_RADIUS"]


def main():
    """ """

    maker = GearMaker()

    svg = SVG_2_GEARS_ANIMATED_TPL % {
        "GEAR": maker.get_gear(),
        "BEARING": maker.get_bearing(),
        "REINFORCMENT": maker.get_reinforcement(),
        "SECOND_GEAR_X_POS": maker.get_second_gear_x_pos(),
        "SECOND_GEAR_X_LEFT": maker.get_second_gear_x_left(),
        "GEAR_MODULE": maker.MODULE,
        "GEAR_NB_TEETH": maker.NB_TEETHS,
        "GEAR_RATIO_GAP_TEETH": maker.RATIO_TEETH_GAP_BASE,
        "GEAR_TEETH_CURVATURE": maker.TEETH_CURVATURE,
        "GEAR_TEETH_RATION_HEAD_BASE": maker.RATIO_TEETH_HEAD_BASE,
        "SECOND_GEAR_ROTATION_ANIM_START": maker.get_second_gear_rotation(),
        "SECOND_GEAR_ROTATION_ANIM_END": maker.get_second_gear_rotation() - 380.0,
        "ANIMATE_PERIOD": 30,
    }

    fp = open("hobbymat_2gears_%d_animated.svg" % GearMaker.NB_TEETHS, "w")
    fp.write(svg)
    fp.close()

    svg = SVG_2_GEARS_STATIC_TPL % {
        "GEAR": maker.get_gear(),
        "BEARING": maker.get_bearing(),
        "REINFORCMENT": maker.get_reinforcement(),
        "SECOND_GEAR_X_POS": maker.get_second_gear_x_pos(),
        "SECOND_GEAR_X_LEFT": maker.get_second_gear_x_left(),
        "GEAR_MODULE": maker.MODULE,
        "GEAR_NB_TEETH": maker.NB_TEETHS,
        "GEAR_RATIO_GAP_TEETH": maker.RATIO_TEETH_GAP_BASE,
        "GEAR_TEETH_CURVATURE": maker.TEETH_CURVATURE,
        "GEAR_TEETH_RATION_HEAD_BASE": maker.RATIO_TEETH_HEAD_BASE,
        "SECOND_GEAR_ROTATION_ANIM_START": maker.get_second_gear_rotation(),
        "SECOND_GEAR_ROTATION_ANIM_END": maker.get_second_gear_rotation() - 380.0,
    }

    fp = open("hobbymat_2gears_%d_static.svg" % GearMaker.NB_TEETHS, "w")
    fp.write(svg)
    fp.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="GearMaker", description="Generate gear")

    # arguments
    parser.add_argument(
        "-m", "--module", dest="module", type=float, default=1.0, help="gear module"
    )
    parser.add_argument(
        "-z",
        "--nb-teeth",
        dest="nb_teeth",
        type=int,
        default=40,
        help="number of teeth",
    )
    parser.add_argument(
        "-r",
        "--ratio-teeth-gap",
        dest="ratio",
        type=float,
        default=0.60,
        help="ratio teeth-gap",
    )
    parser.add_argument(
        "-c",
        "--teeth-curvature",
        dest="teeth_curvature",
        type=float,
        default=5.0,
        help="teeth curvature",
    )
    parser.add_argument(
        "-b",
        "--ratio-teeth-head-base",
        dest="ratio_teeth_head_base",
        type=float,
        default=0.4,
        help="teeth ratio head / base",
    )

    options = parser.parse_args()

    GearMaker.MODULE = options.module
    GearMaker.NB_TEETHS = options.nb_teeth
    GearMaker.RATIO_TEETH_GAP_BASE = options.ratio
    GearMaker.TEETH_CURVATURE = options.teeth_curvature
    GearMaker.RATIO_TEETH_HEAD_BASE = options.ratio_teeth_head_base

    GearMaker.setup()

    main()
