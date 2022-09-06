'''
generate a svg file for a gear with given diameter and nb of teeth

for hobbymat: i think, the modul of the gears is "1"

nb teeth is 30 / 35 / 40 / 50 / 55 / 60 / 65 / 70 / 75 

the ratio between a tooth "base" and an empty space is undefined...
I will take 2 to 1, seems optically good...
'''

from typing import Tuple

import math


SVG_TPL = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="400mm"
   height="400mm"
   viewBox="0 0 400 400"
   version="1.1"
   id="gear_hobbymat">
   <g>
   %(GEAR)s
   %(BEARING)s
   </g>
   
</svg>
'''


class GearMaker:
    '''
    '''
    CENTER = (0, 0) # mm

    # definition of modul
    # MODULE = PITCH_CIRCLE_DIAMETER / NB_TEETHS
    MODULE = 1.0

    # Gear basic size # change me
    NB_TEETHS = 60

    # size of the gear
    PITCH_CIRCLE_DIAMETER = MODULE * NB_TEETHS
    PITCH_CIRCLE_RADIUS   = PITCH_CIRCLE_DIAMETER / 2.0

    # Zähne 
    FOOT_HEIGHT = MODULE * 1.25
    HEAD_HEIGHT = MODULE

    # other radius
    FOOT_CIRCLE_RADIUS = PITCH_CIRCLE_RADIUS - FOOT_HEIGHT # ( NB_TEETHS - 2.5 ) * MODULE / 2.0 # smaller than the PITCH_CICLE_RADIUS
    HEAD_CIRCLE_RADIUS = PITCH_CIRCLE_RADIUS + HEAD_HEIGHT # ( NB_TEETHS + 2.0 ) * MODULE / 2.0 # larger than the PITCH_CICLE_RADIUS
   
    # pitch
    PITCH = MODULE * math.pi  # länge des bogen zwischen 2 Zähne auf den PITCH_CIRCLE : (2pi * R) / z 

    # test teeth profiles
    TEETH_PROFIL = 'BASIC'
    TEETH_PROFIL = 'ADVANCED'
    TEETH_PROFIL = 'ARC'

    # EXACT TEETH ARC RADIUS SIZE
    TEETH_FROFIL_EXACT__ARC_RADIUS = 9.0 / 4.0 * (FOOT_HEIGHT + HEAD_HEIGHT)   # about 5
    # you can adjust it to change the look of the teeth... big value -> straight lines , small value -> round

    # ratio gap/teeth
    RATIO_BASE_TEETH = 8.0 / 4.0  # for  'BASIC' and 'ADVANCED'
    RATIO_BASE_TEETH = 7.0 / 5.0  # for  'ARC'

    BEARING_RADIUS = 10 # mm
    BEARING_NUT_LENGTH = 4 # mm
    BEARING_NUT_HEIGHT = 2 # mm 

    # SVG VIEW
    STROKE_WIDTH = 0.05
    STROKE_COLOR = '#000000'
    GEAR_COLOR = '#cccccc'
    BEARING_COLOR = '#ffcccc'

    def __init__(self):
        '''
        '''
        print(" generating gear for %d teeth" % GearMaker.NB_TEETHS)

        print("NB_TEETHS             : %d"    % GearMaker.NB_TEETHS)
        print("MODULE                : %d"    % GearMaker.MODULE)
        print("PITCH_CIRCLE_DIAMETER : %4.2f" % GearMaker.PITCH_CIRCLE_DIAMETER)
        print("PITCH_CIRCLE_RADIUS   : %4.2f" % GearMaker.PITCH_CIRCLE_RADIUS)
        print("FOOT_HEIGHT           : %4.2f" % GearMaker.FOOT_HEIGHT)
        print("HEAD_HEIGHT           : %4.2f" % GearMaker.HEAD_HEIGHT)
        print("FOOT_CIRCLE_RADIUS    : %4.2f" % GearMaker.FOOT_CIRCLE_RADIUS)
        print("HEAD_CIRCLE_RADIUS    : %4.2f" % GearMaker.HEAD_CIRCLE_RADIUS)
        print("PITCH                 : %4.2f [length of the arc of the pitch cirlce between 3 teeths]" % GearMaker.PITCH)
        print("-> ALPHA FREQ (rad)   : %4.2f" % (GearMaker.PITCH / GearMaker.PITCH_CIRCLE_RADIUS))
        print("-> ALPHA FREQ (deg)   : %4.2f" % ((GearMaker.PITCH / GearMaker.PITCH_CIRCLE_RADIUS) * 180 / math.pi))

        print("coeff  pitch circle diameter / foot circle diameter    : %f" % (self.PITCH_CIRCLE_RADIUS / self.FOOT_CIRCLE_RADIUS))
        print("coeff  head  circle diameter / pitch circle diameter   : %f" % (self.HEAD_CIRCLE_RADIUS / self.PITCH_CIRCLE_RADIUS))

        self.gear_segments = []
        self.bearing_segments = []

        self._start_pt = [0, 0]
        self._curr_pt = [0, 0]
        self._end_pt = [0, 0]

    def rotate(self, pt, angle):
        '''
        '''
        mat = [[math.cos(angle), math.sin(-angle)], [math.sin(angle), math.cos(angle)]]
    
        return  (
            mat[0][0] * pt[0] + mat[0][1]* pt[1], 
            mat[1][0] * pt[0] + mat[1][1]* pt[1]
        )
    
    def translate(self, pt, coeff):
        '''
        '''
        mat = [[coeff, 0.0],[0.0, coeff]]

        return  (
            mat[0][0] * pt[0] + mat[0][1]* pt[1], 
            mat[1][0] * pt[0] + mat[1][1]* pt[1]
        )
        
    def get_gear(self) -> str:
        '''
        '''
        self.make_gear()

        gear_path = " ".join(self.gear_segments)

        path = '''
    <g style="fill:#cccccc" transform="translate(200,200)">
        <path style="fill:%s;stroke:%s;stroke-width:%f"
            d=" %s z"
            id="gear" />
    </g>
        ''' % (self.GEAR_COLOR, self.STROKE_COLOR, self.STROKE_WIDTH, gear_path)

        return path

    def get_bearing(self) -> str:
        '''
        '''
        self.make_bearing()

        bearing_path = " ".join(self.bearing_segments)

        path = '''
    <g style="fill:#ffcccc"  transform="translate(200,200)">
        <path style="fill:%s;stroke:%s;stroke-width:%f"
            d="M %s"
            id="bearing" />
    </g>
        ''' % (self.BEARING_COLOR, self.STROKE_COLOR, self.STROKE_WIDTH, bearing_path)

        return path

    def make_gear(self):
        '''
        '''
        self._start_pt = (self.FOOT_CIRCLE_RADIUS, 0.0)

        initial_move = ''' M  %(start_x)s %(start_y)s      
        ''' % { 'start_x': self._start_pt[0], 'start_y': self._start_pt[1]}
            
        self.gear_segments.append(initial_move)

        for _ in range(self.NB_TEETHS):
            self._make_teeth()

    def _make_teeth(self):
        '''
        '''
        if self.TEETH_PROFIL == 'BASIC':
            self._make_teeth_basic()
        elif self.TEETH_PROFIL == 'ADVANCED':
            self._make_teeth_advanced()
        elif self.TEETH_PROFIL == 'ARC':
            self._make_teeth_arc()
        else:
            print("teeth style unknown!")

    def _make_teeth_basic(self):
        '''
        basic teeth
        '''
        start_pt = self._start_pt

        alpha = self.PITCH / self.PITCH_CIRCLE_RADIUS

        alpha_gap  = (alpha) / (1 + self.RATIO_BASE_TEETH)
        alpha_teeth = (alpha) / (1 + 1.0/self.RATIO_BASE_TEETH)

        gap_pt = self.rotate(start_pt, alpha_gap)

        rotation = 0
        arc_path = 0 # small arc
        clockwise = 1

        # 1- first an arc along the base for the teeth "gap"
        arc = '''A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(gap_x)s %(gap_y)s L 
        ''' % {
            "radius": self.FOOT_CIRCLE_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "gap_x": gap_pt[0],
            "gap_y": gap_pt[1],
        }

        self.gear_segments.append(arc)

        # now the teeth itself
        height_h_coeff = self.HEAD_CIRCLE_RADIUS  / self.FOOT_CIRCLE_RADIUS

        # start the teeth : straight to the head
        teeth_HEAD = self.rotate(gap_pt, alpha_teeth / 4.0)
        teeth_HEAD = self.translate(teeth_HEAD, height_h_coeff)
         
        teeth = '''%(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_HEAD[0], "teeth_y": teeth_HEAD[1] }

        self.gear_segments.append(teeth)

        # teeth HEAD finish
        teeth_HEAD = self.rotate(teeth_HEAD, alpha_teeth/2.0)

        teeth = '''%(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_HEAD[0], "teeth_y": teeth_HEAD[1] }

        self.gear_segments.append(teeth)

        # back to the base : next start
        start_pt = self.rotate(gap_pt, alpha_teeth)

        teeth = '''%(start_pt_x)s %(start_pt_y)s
        ''' % {
            "start_pt_x": start_pt[0]  ,
            "start_pt_y": start_pt[1]  ,           
        }

        self.gear_segments.append(teeth)

        self._start_pt = start_pt

    def _make_teeth_advanced(self):
        '''
        consider the pitch as it should be the case
        '''
        start_pt = self._start_pt

        alpha = self.PITCH / self.PITCH_CIRCLE_RADIUS

        alpha_gap  = (alpha) / (1 + self.RATIO_BASE_TEETH)
        alpha_teeth = (alpha) / (1 + 1.0/self.RATIO_BASE_TEETH)

        gap_pt = self.rotate(start_pt, alpha_gap)

        rotation = 0
        arc_path = 0 # small arc
        clockwise = 1

        # 1- first an arc along the base for the teeth "gap"
        arc = ''' A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(gap_x)s %(gap_y)s
        ''' % {
            "radius": self.FOOT_CIRCLE_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "gap_x": gap_pt[0],
            "gap_y": gap_pt[1],
        }

        self.gear_segments.append(arc)

        # noe the teeth itself
        height_p_coeff = self.PITCH_CIRCLE_RADIUS / self.FOOT_CIRCLE_RADIUS
        height_h_coeff = self.HEAD_CIRCLE_RADIUS  / self.PITCH_CIRCLE_RADIUS

        # start the teeth : Pitch
        teeth_PITCH = self.rotate(gap_pt, alpha_teeth / 8.0)
        teeth_PITCH = self.translate(teeth_PITCH, height_p_coeff)
         
        teeth = ''' L %(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_PITCH[0], "teeth_y": teeth_PITCH[1] }

        self.gear_segments.append(teeth)

        # teeth HEAD
        teeth_HEAD = self.rotate(teeth_PITCH, alpha_teeth/4.0)
        teeth_HEAD = self.translate(teeth_HEAD, height_h_coeff)

        teeth = '''%(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_HEAD[0], "teeth_y": teeth_HEAD[1] }

        self.gear_segments.append(teeth)

        # teeth HEAD finish
        teeth_HEAD = self.rotate(teeth_HEAD, alpha_teeth/4.0)

        teeth = '''%(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_HEAD[0], "teeth_y": teeth_HEAD[1] }

        self.gear_segments.append(teeth)

        # teeth PITCH finish
        teeth_PITCH = self.translate(teeth_HEAD, 1.0/height_h_coeff)
        teeth_PITCH = self.rotate(teeth_PITCH, alpha_teeth/4.0)
           
        teeth = '''%(teeth_x)s %(teeth_y)s ''' % { "teeth_x": teeth_PITCH[0], "teeth_y": teeth_PITCH[1] }

        self.gear_segments.append(teeth)

        # back to the base : next start
        start_pt = self.rotate(gap_pt, alpha_teeth)

        teeth = '''%(start_pt_x)s %(start_pt_y)s
        ''' % {
            "start_pt_x": start_pt[0]  ,
            "start_pt_y": start_pt[1]  ,           
        }

        self.gear_segments.append(teeth)

        self._start_pt = start_pt

    def _make_teeth_arc(self):
        '''
        exact teeth
        '''
        start_pt = self._start_pt

        alpha = self.PITCH / self.PITCH_CIRCLE_RADIUS

        alpha_gap =   (alpha) / (1 + self.RATIO_BASE_TEETH)
        alpha_teeth = (alpha) / (1 + 1.0/self.RATIO_BASE_TEETH)

        gap_pt = self.rotate(start_pt, alpha_gap)

        rotation = 0
        arc_path = 0 # small arc
        clockwise = 1

        # 1- first an arc along the base for the teeth "gap"
        arc = ''' A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(gap_x)s %(gap_y)s
        ''' % {
            "radius": self.FOOT_CIRCLE_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "gap_x": gap_pt[0],
            "gap_y": gap_pt[1],
        }

        self.gear_segments.append(arc)

        # now the teeth itself -  arc to the head
        arc_start = gap_pt
        arc_end = self.rotate(arc_start, 2.0*alpha_teeth/7.0)
        arc_end = self.translate(arc_end, self.HEAD_CIRCLE_RADIUS  / self.FOOT_CIRCLE_RADIUS)
        ARC_RADIUS = self.TEETH_FROFIL_EXACT__ARC_RADIUS
        ARC_RADIUS = 4 # changed per hand

        arc = ''' A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(arc_end_x)s %(arc_end_y)s
        ''' % {
            "radius": ARC_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "arc_end_x": arc_end[0],
            "arc_end_y": arc_end[1],
        }

        self.gear_segments.append(arc)

        # teeth HEAD - you could make an arc
        teeth_HEAD = self.rotate(arc_end, 3.0*alpha_teeth/7.0)

        teeth = ''' L %(teeth_x)s %(teeth_y)s 
        ''' % { "teeth_x": teeth_HEAD[0], "teeth_y": teeth_HEAD[1] }

        self.gear_segments.append(teeth)

        # arc to the base
        arc_start = teeth_HEAD
        arc_end = self.rotate(arc_start, 2.0*alpha_teeth/7.0)
        arc_end = self.translate(arc_end, self.FOOT_CIRCLE_RADIUS  / self.HEAD_CIRCLE_RADIUS)

        # back to the base : arc to the base
        arc = ''' A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(arc_end_x)s %(arc_end_y)s
        
        ''' % {
            "radius": ARC_RADIUS,
            "rotation": rotation,
            "arc_path": arc_path,
            "clockwise": clockwise,
            "arc_end_x": arc_end[0],
            "arc_end_y": arc_end[1],
        }

        self.gear_segments.append(arc)

        self._start_pt = arc_end

    def make_bearing(self):
        '''
        '''
        alpha1 = math.pi / 2 - math.atan((self.BEARING_NUT_LENGTH/2.0) / self.BEARING_RADIUS)
        alpha2 = math.pi / 2 + math.atan((self.BEARING_NUT_LENGTH/2.0) / self.BEARING_RADIUS)

        #print(alpha1 / math.pi * 180)
        #print(alpha2 / math.pi * 180)

        pt = (self.BEARING_RADIUS, 0)
        pt_A = self.rotate(pt, alpha1)
        pt_B = self.rotate(pt, alpha2)

        arc = '''%(start_pt_x)s %(start_pt_y)s A %(radius)s %(radius)s %(rotation)s %(arc_path)s %(clockwise)s %(end_pt_x)s %(end_pt_y)s
            ''' % {
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

        nut = ''' L %(x1)s %(y1)s  %(x2)s %(y2)s  %(x3)s %(y3)s''' % {
            'x1': pt_B[0],
            'y1': pt_B[1] + self.BEARING_NUT_HEIGHT,
            'x2': pt_A[0],
            'y2': pt_B[1] + self.BEARING_NUT_HEIGHT,
            'x3': pt_A[0],
            'y3': pt_A[1],
        }

        self.bearing_segments.append(nut)


def main():
    '''
    '''

    gearMaker = GearMaker()

    svg = SVG_TPL % { 'GEAR': gearMaker.get_gear(), 'BEARING': gearMaker.get_bearing()}

    fp = open("hobbymat_gear_%d.svg" % GearMaker.NB_TEETHS, "w")
    fp.write(svg)
    fp.close()


if __name__ == '__main__':
    main()