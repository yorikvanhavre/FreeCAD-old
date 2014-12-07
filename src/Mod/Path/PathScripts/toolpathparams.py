import FreeCADGui as Gui
import FreeCAD as App


class DepthParams():
    ''' DepthParams similar to HeeksCNC
    how to use:
    do = FreeCAD.ActiveDocument.addObject("App::FeaturePython","DepthParms")
    DepthParams(do)
    ViewProviderDepthParams(do.ViewObject)
    App.activeDocument().recompute()
    '''

    def __init__(self,obj):

    #App::PropertyFloat
        #obj.addProperty("App::PropertyInteger", "ToolNo", "Depth Parameters", "Tool Number")
        obj.addProperty("App::PropertyFloat", "ClearanceHeight", "Depth Parameters", "Clearance Height")
        #obj.addProperty("App::PropertyFloat", "StartDepth", "Depth Parameters", "Top of Part")
        obj.addProperty("App::PropertyFloat", "StepDown", "Depth Parameters", "Incremental Step Down of Tool")
        obj.addProperty("App::PropertyFloat", "FinalDepth", "Depth Parameters", "Final Depth of Tool")
        obj.addProperty("App::PropertyFloat", "RetractHeight", "Depth Parameters", "Retract Height")
        #obj.addProperty("App::PropertyEnumeration", "AbsIncrMode", "Depth Parameters", "Abs/Incr Mode")
        #obj.AbsIncrMode = ['Absolute','Incremental']
        obj.Proxy = self

    def execute(self,obj):
        pass

class _DepthParamsPanel:
    '''The editmode TaskPanel for DepthParams objects '''
    def __init__(self):
        
        self.obj = None
        self.form = QtGui.QWidget()
        self.form.setObjectName("TaskPanel")
        self.grid = QtGui.QGridLayout(self.form)
        self.grid.setObjectName("grid")
        self.title = QtGui.QLabel(self.form)
        self.grid.addWidget(self.title, 0, 0, 1, 2)

        # tree
        self.tree = QtGui.QTreeWidget(self.form)
        self.grid.addWidget(self.tree, 1, 0, 1, 2)
        self.tree.setColumnCount(3)
        self.tree.header().resizeSection(0,50)
        self.tree.header().resizeSection(1,80)
        self.tree.header().resizeSection(2,60)
        
        # buttons       
        self.addButton = QtGui.QPushButton(self.form)
        self.addButton.setObjectName("addButton")
        self.addButton.setIcon(QtGui.QIcon(":/icons/Arch_Add.svg"))
        self.grid.addWidget(self.addButton, 3, 0, 1, 1)
        self.addButton.setEnabled(True)

        self.delButton = QtGui.QPushButton(self.form)
        self.delButton.setObjectName("delButton")
        self.delButton.setIcon(QtGui.QIcon(":/icons/Arch_Remove.svg"))
        self.grid.addWidget(self.delButton, 3, 1, 1, 1)
        self.delButton.setEnabled(True)

        #QtCore.QObject.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.addElement)
        #QtCore.QObject.connect(self.delButton, QtCore.SIGNAL("clicked()"), self.removeElement)
        #self.update()

class ViewProviderDepthParams:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self
  
    def setEdit(self,vobj,mode):
        taskd = _DepthParamsPanel()
        #taskd.obj = vobj.Object
        #taskd.update()
        FreeCADGui.Control.showDialog(taskd)
        return True


    def unsetEdit(self,vobj,mode):
        FreeCADGui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def getIcon(self):
        return """
        /* XPM */
        static char * Parameters_xpm[] = {
        "16 16 22 1",
        " 	c None",
        ".	c #141010",
        "+	c #000000",
        "@	c #FFFFFF",
        "#	c #FBFBFB",
        "$	c #FDFDFD",
        "%	c #F5F5F5",
        "&	c #FEFEFE",
        "*	c #020202",
        "=	c #2F2F2F",
            "-	c #F9F9F9",
            ";	c #F1F1F1",
            ">	c #EFEFEF",
            ",	c #070707",
            "'	c #050505",
            ")	c #090909",
            "!	c #F8F8F8",
            "~	c #101010",
            "{	c #404040",
            "]	c #0C0C0C",
            "^	c #FEFDFE",
            "/	c #0A0808",
            "   ........+++  ",
            "   .@@@@@@#@@+  ",
            "   .@....@@@$+  ",
            "   .@@@@%@@&@.  ",
            "   .@...*+=$@.  ",
            "   .@@@@@@@-@.  ",
            "   .@....;;.@.  ",
            "   .@>%@@@@@@.  ",
            "   .@=,')+)@@.  ",
            "   .@!@@@@@@@)  ",
            "   .@)+~{%++@]  ",
            "   .@@@@@@@^@/  ",
            "   .@+'')@++@+  ",
            "   .@@@@@@@@@]  ",
            "   .@@@&&@@@@.  ",
            "   ...........  "};
                        """
#'''
#how to use:
#do = FreeCAD.ActiveDocument.addObject("App::FeaturePython","DepthParms")
#DepthParams(do)
#ViewProviderDepthParams(do.ViewObject)
#App.activeDocument().recompute()
#'''

class ToolParams():
    def __init__(self,obj):
    #App::PropertyFloat
        obj.addProperty("App::PropertyInteger", "ToolNo", "Tool Parameters", "Tool Number")
        obj.addProperty("App::PropertyFloat", "Diameter", "Tool Parameters", "Diameter at End of Tool")
        obj.addProperty("App::PropertyFloat", "FeedVertical", "Tool Parameters", "Vertical Feed Rate")
        obj.addProperty("App::PropertyFloat", "FeedHorizontal", "Tool Parameters", "Horizontal Feed Rate")
        obj.addProperty("App::PropertyFloat", "SpindleSpeed", "Tool Parameters", "Speed of Spindle in RPM")
        #obj.addProperty("App::PropertyFloat", "FinalDepth", "Toolh Parameters", "Final Depth of Tool")
        #obj.addProperty("App::PropertyFloat", "RetractHeight", "Tool Parameters", "Retract Height")
        #obj.addProperty("App::PropertyEnumeration", "AbsIncrMode", "Depth Parameters", "Abs/Incr Mode")
        #obj.AbsIncrMode = ['Absolute','Incremental']
        obj.Proxy = self

    def execute(self,obj):
        pass

class ViewProviderToolParams:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"

        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def getIcon(self):
        return """
        /* XPM */
        static char * tools_xpm[] = {
        "16 16 85 1",
        " 	c None",
        ".	c #4A4A4A",
        "+	c #424242",
        "@	c #212121",
            "#	c #1E1E1E",
            "$	c #888888",
            "%	c #434343",
            "&	c #4F4F4F",
            "*	c #383838",
            "=	c #757575",
            "-	c #454545",
            ";	c #4E4E4E",
            ">	c #333333",
            ",	c #414141",
            "'	c #696969",
            ")	c #242424",
            "!	c #3D3D3D",
            "~	c #515151",
            "{	c #474747",
            "]	c #4C4C4C",
            "^	c #141414",
            "/	c #676767",
            "(	c #3B3B3B",
            "_	c #232323",
            ":	c #525252",
            "<	c #575757",
            "[	c #464646",
            "}	c #404040",
            "|	c #111111",
            "1	c #282828",
            "2	c #7F7F7F",
            "3	c #3F3F3F",
            "4	c #2E2E2E",
            "5	c #4B4B4B",
            "6	c #2A2A2A",
            "7	c #494949",
            "8	c #313131",
            "9	c #323232",
            "0	c #6D6D6D",
            "a	c #4D4D4D",
            "b	c #202020",
            "c	c #292929",
            "d	c #272727",
            "e	c #0B0B0B",
            "f	c #161616",
            "g	c #484848",
            "h	c #2B2B2B",
            "i	c #606060",
            "j	c #1A1A1A",
            "k	c #5E5E5E",
            "l	c #3E3E3E",
            "m	c #3A3A3A",
            "n	c #626262",
            "o	c #616161",
            "p	c #5F5F5F",
            "q	c #585858",
            "r	c #5D5D5D",
            "s	c #1C1C1C",
            "t	c #303030",
            "u	c #9D9D9D",
            "v	c #7B7B7B",
            "w	c #555555",
            "x	c #5C5C5C",
            "y	c #505050",
            "z	c #999999",
            "A	c #7A7A7A",
            "B	c #656565",
            "C	c #9E9E9E",
            "D	c #848484",
            "E	c #989898",
            "F	c #545454",
            "G	c #8D8D8D",
            "H	c #363636",
            "I	c #979797",
            "J	c #2D2D2D",
            "K	c #717171",
            "L	c #9C9C9C",
            "M	c #747474",
            "N	c #9A9A9A",
            "O	c #A0A0A0",
            "P	c #353535",
            "Q	c #959595",
            "R	c #9B9B9B",
            "S	c #131313",
            "T	c #222222",
            "      .+@#      ",
            "      $%&*      ",
            "      =-;>      ",
            ",')!  ~{]^  /*(_",
            ":<[&  _;}| 123&4",
            "{3&5  6789  0[ab",
            "8{;@  c3{d  {][e",
            "fg-h   }i   >&8^",
            "j;95  ,k]   (lmd",
            " >7!  9nop  6(q ",
            " (rs  tauv  ):w ",
            "1xry  t$zA  aB% ",
            "bpyC  dDEF  lgGw",
            "1HIuJ  e4   mKLi",
            "@MNO)       PQRk",
            "S3Qx        TAD "};
                        """
'''
how to use:
tl = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Tools")
ToolParams(tl)
ViewProviderToolParams(tl.ViewObject)
App.activeDocument().recompute()
'''

class FixtureParams():
    def __init__(self,obj):

        obj.addProperty("App::PropertyEnumeration", "Fixture", "Fixture Parameters", "Fixture Mode")
        obj.Fixture = ['G54','G55','G56','G57','G58','G59']
        obj.Proxy = self

    def execute(self,obj):
        pass

class ViewProviderFixtureParams:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


    def getIcon(self):
        return """
        /* XPM */
        static char * fixtures_xpm[] = {
        "16 16 14 1",
        " 	c None",
        ".	c #FF0000",
        "+	c #FE0000",
        "@	c #0000FF",
        "#	c #0000FE",
        "$	c #1900E5",
            "%	c #BE0040",
            "&	c #61009D",
            "*	c #A0005E",
            "=	c #F90005",
            "-	c #1400EA",
            ";	c #3400CA",
            ">	c #650099",
            ",	c #AD0051",
            "                ",
            "                ",
            "     ..         ",
            "                ",
            "    +  + ..     ",
            "        .       ",
            "   +    .  +    ",
            "                ",
            "  . @#$% &  .   ",
            " .    *   *     ",
            "      = @@-; .  ",
            ".    ... >,.  . ",
            "                ",
            "    ..  +..+....",
            "                ",
            "                "};
                        """
'''
how to use:
fl = FreeCAD.ActiveDocument.addObject("App::FeaturePython","FixtureOffset")
FixtureParams(fl)
ViewProviderFixtureParams(fl.ViewObject)
App.activeDocument().recompute()
'''


class CustomObject():
    def __init__(self,obj):
        obj.addProperty("App::PropertyStringList","CustomProps","Base", "A placeholder for custom properties")
        obj.Proxy = self
    def execute(self,obj):
        pass

class ViewProviderCustomObject:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def getIcon(self):
        return """
        /* XPM */
        static char * Parameters_xpm[] = {
        "16 16 22 1",
        " 	c None",
            ".	c #141010",
            "+	c #000000",
            "@	c #FFFFFF",
            "#	c #FBFBFB",
            "$	c #FDFDFD",
            "%	c #F5F5F5",
            "&	c #FEFEFE",
            "*	c #020202",
            "=	c #2F2F2F",
            "-	c #F9F9F9",
            ";	c #F1F1F1",
            ">	c #EFEFEF",
            ",	c #070707",
            "'	c #050505",
            ")	c #090909",
            "!	c #F8F8F8",
            "~	c #101010",
            "{	c #404040",
            "]	c #0C0C0C",
            "^	c #FEFDFE",
            "/	c #0A0808",
            "   ........+++  ",
            "   .@@@@@@#@@+  ",
            "   .@....@@@$+  ",
            "   .@@@@%@@&@.  ",
            "   .@...*+=$@.  ",
            "   .@@@@@@@-@.  ",
            "   .@....;;.@.  ",
            "   .@>%@@@@@@.  ",
            "   .@=,')+)@@.  ",
            "   .@!@@@@@@@)  ",
            "   .@)+~{%++@]  ",
            "   .@@@@@@@^@/  ",
            "   .@+'')@++@+  ",
            "   .@@@@@@@@@]  ",
            "   .@@@&&@@@@.  ",
            "   ...........  "};
                        """

''' example useage:
# create one in the current doc
import toolpathparams
myobj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","header")
toolpathparams.CustomObject(myobj)
toolpathparams.ViewProviderCustomObject(myobj.ViewObject)
# set some properties
myobj.CustomProps = ["import sys","sys.path.insert(0,'/usr/lib/heekscnc/')","import math","import area"]
App.activeDocument().recompute()
'''


class ProfileParams():
    def __init__(self,obj):

        obj.addProperty("App::PropertyEnumeration", "Side", "Profile Parameters", "Side of Line")
        obj.addProperty("App::PropertyFloat", "RollRadius", "Profile Parameters", "Radius at start and end")
        obj.addProperty("App::PropertyFloat", "OffsetExtra", "Profile Parameters", "Extra value to stay off from profile")
        obj.addProperty("App::PropertyFloat", "extend_at_start", "Profile Parameters", "extend_at_start")
        obj.addProperty("App::PropertyFloat", "extend_at_end", "Profile Parameters", "extend_at_end")
        obj.addProperty("App::PropertyFloat", "lead_in_line_len", "Profile Parameters", "lead_in_line_len")
        obj.addProperty("App::PropertyFloat", "lead_out_line_len", "Profile Parameters", "lead_out_line_len")
        obj.Side = ['left','right','on']
        obj.Proxy = self

    def execute(self,obj):
        pass

class ViewProviderProfileParams:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


    def getIcon(self):
        return """
        /* XPM */
        static char * profile_xpm[] = {
        "18 16 6 1",
        " 	c None",
        ".	c #00FF00",
        "+	c #00F800",
        "@	c #00E900",
        "#	c #000000",
            "$	c #00FE00",
            "  .+@@@@@@@@@@+.  ",
            "  . ########## .  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .#          #.  ",
            "  .            .  ",
            "  $            $  ",
            " .             $. ",
            "..              .."};
            """

'''
how to use:
prof1 = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Profile")
ProfileParams(prof1)
ViewProviderProfileParams(prof1.ViewObject)
App.activeDocument().recompute()
'''

class OriginalGeometry:
    def __init__(self,obj):
        self.original =  Gui.Selection.getSelection()[0]
        obj.addProperty("App::PropertyLink","Base","Geometry Properties", "The base object this 2D view must represent")
        obj.addProperty("App::PropertyString", "OriginalObjectName", "Geometry Properties", "Original Geometry")
        obj.OriginalObjectName = self.original.Label
        obj.setEditorMode("OriginalObjectName", 1)

        obj.Proxy = self

    def execute(self,obj):
        pass

class ViewProviderOriginalGeometry:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def getIcon(self):
        return """
        /* XPM */
        static char * Part_Parameters_xpm[] = {
"64 64 419 2",
"  	c None",
". 	c #000102",
"+ 	c #000000",
"@ 	c #000001",
"# 	c #000101",
"$ 	c #03080F",
"% 	c #184786",
"& 	c #153C70",
"* 	c #071425",
"= 	c #010205",
"- 	c #123566",
"; 	c #2875DE",
"> 	c #2C7FEE",
", 	c #2C80EE",
"' 	c #2D82EF",
") 	c #2974D4",
"! 	c #1C5090",
"~ 	c #0E2847",
"{ 	c #010204",
"] 	c #010103",
"^ 	c #000103",
"/ 	c #071529",
"( 	c #205FB5",
"_ 	c #2B7CEC",
": 	c #2B7EED",
"< 	c #2D81EF",
"[ 	c #2E84F0",
"} 	c #2E85F1",
"| 	c #2F87F1",
"1 	c #2A7BD9",
"2 	c #1C5290",
"3 	c #0D2643",
"4 	c #010305",
"5 	c #010203",
"6 	c #02060C",
"7 	c #174383",
"8 	c #2978E7",
"9 	c #2A7BEC",
"0 	c #2B7DED",
"a 	c #2C7EED",
"b 	c #2E83F0",
"c 	c #2E85F0",
"d 	c #2F88F2",
"e 	c #308AF2",
"f 	c #308BF3",
"g 	c #318DF4",
"h 	c #2F86E7",
"i 	c #215E9F",
"j 	c #113153",
"k 	c #02060A",
"l 	c #113365",
"m 	c #266FDA",
"n 	c #2979EB",
"o 	c #2F89F2",
"p 	c #308AF3",
"q 	c #318CF3",
"r 	c #328FF5",
"s 	c #3291F6",
"t 	c #3392F6",
"u 	c #3392F4",
"v 	c #2872BE",
"w 	c #194674",
"x 	c #071421",
"y 	c #091A34",
"z 	c #205DB9",
"A 	c #2977EA",
"B 	c #2978EB",
"C 	c #2A7AEB",
"D 	c #2D83EF",
"E 	c #328EF5",
"F 	c #3290F5",
"G 	c #3391F6",
"H 	c #3393F7",
"I 	c #3494F7",
"J 	c #3496F8",
"K 	c #3597F9",
"L 	c #3698F7",
"M 	c #2A77C0",
"N 	c #194772",
"O 	c #071420",
"P 	c #050D1A",
"Q 	c #194A95",
"R 	c #2874E8",
"S 	c #2876E9",
"T 	c #2A7AEC",
"U 	c #3495F8",
"V 	c #3597F8",
"W 	c #3598F9",
"X 	c #369AFA",
"Y 	c #379CFB",
"Z 	c #2E81D0",
"` 	c #1C5081",
" .	c #0B1E30",
"..	c #03070F",
"+.	c #153E81",
"@.	c #266FE2",
"#.	c #2773E8",
"$.	c #2875E9",
"%.	c #2E86F1",
"&.	c #3089F2",
"*.	c #3699F9",
"=.	c #318BDF",
"-.	c #205C94",
";.	c #0F2B46",
">.	c #010406",
",.	c #010307",
"'.	c #12346D",
").	c #2468D9",
"!.	c #2771E7",
"~.	c #2874E9",
"{.	c #3494EE",
"].	c #215F99",
"^.	c #0F2A5A",
"/.	c #2161CE",
"(.	c #266EE6",
"_.	c #2670E7",
":.	c #2772E8",
"<.	c #2976EA",
"[.	c #2978EA",
"}.	c #2A79EB",
"|.	c #318CF4",
"1.	c #318EF4",
"2.	c #369AF7",
"3.	c #215C95",
"4.	c #040B11",
"5.	c #0E2A5B",
"6.	c #205EC9",
"7.	c #256CE5",
"8.	c #256DE6",
"9.	c #266FE6",
"0.	c #2671E7",
"a.	c #3596F8",
"b.	c #3699FA",
"c.	c #2568A7",
"d.	c #02060B",
"e.	c #1C518E",
"f.	c #143862",
"g.	c #091B3B",
"h.	c #1C53B6",
"i.	c #2469E4",
"j.	c #256BE5",
"k.	c #2C7ECB",
"l.	c #0D263D",
"m.	c #143865",
"n.	c #2E86EE",
"o.	c #051024",
"p.	c #17469C",
"q.	c #2367E3",
"r.	c #246AE4",
"s.	c #369BFA",
"t.	c #3390E7",
"u.	c #174168",
"v.	c #0B1F39",
"w.	c #2976D7",
"x.	c #061127",
"y.	c #1B52B7",
"z.	c #2366E3",
"A.	c #2368E3",
"B.	c #246BE5",
"C.	c #256EE6",
"D.	c #3598F4",
"E.	c #1E5589",
"F.	c #03080C",
"G.	c #05101E",
"H.	c #2261B7",
"I.	c #000104",
"J.	c #040D1C",
"K.	c #102F67",
"L.	c #1C51AE",
"M.	c #256BE3",
"N.	c #2569A9",
"O.	c #07131F",
"P.	c #19498E",
"Q.	c #0B27AE",
"R.	c #0B25A1",
"S.	c #051148",
"T.	c #010410",
"U.	c #02060D",
"V.	c #0C254D",
"W.	c #184692",
"X.	c #256BDA",
"Y.	c #2A76BE",
"Z.	c #12376C",
"`.	c #2976E8",
" +	c #143861",
".+	c #0B26AD",
"++	c #0D2DC9",
"@+	c #0E2EC9",
"#+	c #0E2FCA",
"$+	c #0C29AA",
"%+	c #06134D",
"&+	c #010513",
"*+	c #010306",
"=+	c #0B1F3E",
"-+	c #174284",
";+	c #256CD4",
">+	c #3087DA",
",+	c #102E4B",
"'+	c #0C2349",
")+	c #256DDB",
"!+	c #0A24AD",
"~+	c #0D2BC8",
"{+	c #0D2CC8",
"]+	c #0E30CA",
"^+	c #0F31CB",
"/+	c #0D2DB7",
"(+	c #07175B",
"_+	c #02071A",
":+	c #091B35",
"<+	c #16427E",
"[+	c #256AC9",
"}+	c #3391EB",
"|+	c #18436C",
"1+	c #061329",
"2+	c #205DC3",
"3+	c #0A24AC",
"4+	c #0C2AC8",
"5+	c #0E2FC9",
"6+	c #0E31CA",
"7+	c #0F32CB",
"8+	c #0F33CB",
"9+	c #0F31C3",
"0+	c #081C6C",
"a+	c #030922",
"b+	c #153C6F",
"c+	c #2263B7",
"d+	c #2E82EF",
"e+	c #3496F5",
"f+	c #1E568D",
"g+	c #040A10",
"h+	c #030812",
"i+	c #19499F",
"j+	c #0A23AC",
"k+	c #0C29C7",
"l+	c #0C2AC7",
"m+	c #0C2BC8",
"n+	c #1034CC",
"o+	c #1035CC",
"p+	c #1036CD",
"q+	c #0C268D",
"r+	c #040F37",
"s+	c #01030A",
"t+	c #050F1A",
"u+	c #143968",
"v+	c #2263B1",
"w+	c #2E87EE",
"x+	c #256BAF",
"y+	c #081725",
"z+	c #102F69",
"A+	c #2265DF",
"B+	c #0A21AC",
"C+	c #0B27C6",
"D+	c #0B28C7",
"E+	c #1137CD",
"F+	c #1138CE",
"G+	c #0E2C9F",
"H+	c #061446",
"I+	c #020511",
"J+	c #03090F",
"K+	c #123359",
"L+	c #215EA3",
"M+	c #3088EA",
"N+	c #2B7ACB",
"O+	c #0E2741",
"P+	c #0B224F",
"Q+	c #205ED7",
"R+	c #2264E2",
"S+	c #0920AB",
"T+	c #0A26C5",
"U+	c #1136CD",
"V+	c #1239CE",
"W+	c #123ACE",
"X+	c #0F30A9",
"Y+	c #07154B",
"Z+	c #020512",
"`+	c #03080D",
" @	c #123459",
".@	c #2262A6",
"+@	c #184370",
"@@	c #06112A",
"#@	c #1B50BD",
"$@	c #2060E0",
"%@	c #2162E1",
"&@	c #091EAA",
"*@	c #0A24C5",
"=@	c #0B28C6",
"-@	c #123ACF",
";@	c #133BCF",
">@	c #1136BC",
",@	c #081C5E",
"'@	c #03081C",
")@	c #02060E",
"!@	c #133B92",
"~@	c #1E5BDD",
"{@	c #1F5EDF",
"]@	c #081DAA",
"^@	c #0A23C4",
"/@	c #0A25C5",
"(@	c #0B26C6",
"_@	c #133CD0",
":@	c #133DD0",
"<@	c #133CC9",
"[@	c #01040C",
"}@	c #02040A",
"|@	c #1D55D9",
"1@	c #1E59DD",
"2@	c #081DA9",
"3@	c #0922C4",
"4@	c #0923C4",
"5@	c #123BCF",
"6@	c #133CCF",
"7@	c #020613",
"8@	c #02060F",
"9@	c #1D56DB",
"0@	c #071BA8",
"a@	c #0820C3",
"b@	c #0921C3",
"c@	c #1F5DDE",
"d@	c #2162E0",
"e@	c #266FE7",
"f@	c #133861",
"g@	c #061AA8",
"h@	c #081FC2",
"i@	c #020614",
"j@	c #1D58DC",
"k@	c #0618A7",
"l@	c #071EC2",
"m@	c #0517A7",
"n@	c #071CC1",
"o@	c #071DC2",
"p@	c #081EC2",
"q@	c #020615",
"r@	c #113257",
"s@	c #0517A6",
"t@	c #061BC0",
"u@	c #071DC1",
"v@	c #020616",
"w@	c #2771CA",
"x@	c #0E2745",
"y@	c #000304",
"z@	c #0516A6",
"A@	c #0619C0",
"B@	c #061AC0",
"C@	c #1C56DB",
"D@	c #205FDF",
"E@	c #2264E1",
"F@	c #2872D2",
"G@	c #0F2C50",
"H@	c #061BC1",
"I@	c #020617",
"J@	c #2977E1",
"K@	c #153B6F",
"L@	c #010408",
"M@	c #2978E8",
"N@	c #194A8E",
"O@	c #040B15",
"P@	c #05149A",
"Q@	c #1F58AF",
"R@	c #08172D",
"S@	c #01062B",
"T@	c #030E68",
"U@	c #0515A4",
"V@	c #020517",
"W@	c #205FC1",
"X@	c #0B1F3D",
"Y@	c #01041D",
"Z@	c #030C5B",
"`@	c #051498",
" #	c #0619BF",
".#	c #020516",
"+#	c #2161E0",
"@#	c #2266E2",
"##	c #2264D2",
"$#	c #0F2C5C",
"%#	c #00010C",
"&#	c #020946",
"*#	c #041180",
"=#	c #061AB7",
"-#	c #020515",
";#	c #2265DD",
">#	c #13397A",
",#	c #000002",
"'#	c #000105",
")#	c #020839",
"!#	c #041074",
"~#	c #061AAF",
"{#	c #020514",
"]#	c #194AA4",
"^#	c #051023",
"/#	c #02062C",
"(#	c #040F67",
"_#	c #071AA5",
":#	c #010414",
"<#	c #1C53BF",
"[#	c #0A1E43",
"}#	c #01051E",
"|#	c #040E5B",
"1#	c #061895",
"2#	c #0921C2",
"3#	c #010413",
"4#	c #1C55CC",
"5#	c #0C2351",
"6#	c #010315",
"7#	c #040D4E",
"8#	c #061889",
"9#	c #0A22C0",
"0#	c #010412",
"a#	c #1C55DB",
"b#	c #1C56D7",
"c#	c #103076",
"d#	c #02050D",
"e#	c #01020C",
"f#	c #030C41",
"g#	c #06177C",
"h#	c #0923BB",
"i#	c #010311",
"j#	c #143C9B",
"k#	c #040D20",
"l#	c #000108",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                      . + @ #                                                                   ",
"                                                  + @ $ % & * + + = +                                                           ",
"                                                . . - ; > , ' ) ! ~ { + ] +                                                     ",
"                                            ^ + / ( _ : > < ' [ } | 1 2 3 4 + 5 +                                               ",
"                                        + @ 6 7 8 9 0 a , < b c | d e f g h i j k + . +                                         ",
"                                    + . ^ l m n 9 _ : > < ' [ } | o p q g r s t u v w x + + . +                                 ",
"                                  . + y z A B C 9 0 a , < D [ | d e f g E F G H I J K L M N O + + . +                           ",
"                              # + P Q R S A n T _ 0 > < ' [ } | o p q g r F t I U V W X Y Y Y Z `  .@ + 5 +                     ",
"                          # + ..+.@.#.$.A B C 9 0 a , < D [ %.d &.f g E F G H I J K *.X Y Y Y Y Y Y =.-.;.>.+ 5 +               ",
"                      + @ ,.'.).!.#.~.S A n T _ 0 > , ' [ } | o p q g r F t H U V W X Y Y Y Y Y Y Y Y Y Y {.].k + #             ",
"                  + . ^ ^./.(._.:.#.$.<.[.}.9 0 a , < D [ %.d &.f |.1.F G H I J K *.X Y Y Y Y Y Y Y Y Y 2.3.4.+ . .             ",
"              + . # 5.6.7.8.9.0.#.~.S A n T _ 0 > , ' b c | o p q g r F t H U a.W b.Y Y Y Y Y Y Y Y Y c.O + d.e.f..             ",
"            . + g.h.i.j.8.(._.:.#.$.<.[.}.9 _ : , < D [ %.d &.f |.1.r s t I J K *.X Y Y Y Y Y Y Y k.l.+ 4 m.n.e f..             ",
"        ^ + o.p.q.i.r.7.8.9.0.:.~.$.A n T _ 0 > , ' b c | d e q g r F t H U a.W b.s.Y Y Y Y Y t.u.5 . v.w.c d e f..             ",
"    + + + x.y.z.A.i.B.7.C._.:.#.$.<.[.}.9 _ : > < D [ %.d &.f |.1.r s t I U K *.X Y Y Y Y D.E.F.@ G.H., D c d e f..             ",
"      + I.+ + J.K.L.M.8.9.0.:.~.$.A B C _ 0 > , ' b c | d e f g E F t H U a.W b.s.Y Y Y N.O.+ d.P._ a , D c d e f..             ",
"      + Q.R.S.T.@ + U.V.W.X.#.$.<.[.}.9 _ : > < ' [ } d &.f |.1.r s t I U V W X Y Y Y. .+ 4 Z.`.}._ : , ' c | e  +.             ",
"      + .+++@+#+$+%+&+# + *+=+-+;+B C 9 0 a , ' b c | d e f g E F G H U a.W b.s.>+,++ 5 '+)+$.A }._ : , ' c | e  +.             ",
"      + !+~+{+@+#+]+^+/+(+_+. + # :+<+[+: > < ' [ } | o p |.1.r s t I U V W }+|+4 . 1+2+_.#.$.A }._ : , ' c | e  +.             ",
"      + 3+4+~+{+++5+]+6+7+8+9+0+a+I.+ + * b+c+d+c | d e f g E F G H I J e+f+g++ h+i+j.C._.#.$.A }._ : , ' c | e  +.             ",
"      + j+k+l+m+{+++@+]+6+7+8+n+o+p+q+r+s++ + t+u+v+w+p q g r s t I U x+y++ 4 z+A+i.j.C._.#.$.A }._ : , ' c | e  +.             ",
"      + B+C+D+k+4+{+++@+#+]+^+7+n+o+p+E+F+G+H+I+# + J+K+L+M+F G H N+O++ 5 P+Q+R+q.i.j.8._.:.$.A }.9 : , ' [ | &. +.             ",
"      + S+T+C+D+k+4+~+{+++5+]+^+7+8+n+o+U+E+V+W+X+Y+Z+# + `+ @.@+@{ # @@#@$@%@R+q.i.j.8._.:.$.A }.9 : , ' [ | &. +.             ",
"      + &@*@T+C+=@k+l+m+{+++5+]+6+7+8+n+o+U+E+F+V+-@;@>@,@'@] + + )@!@~@{@$@%@R+q.i.j.8._.:.$.A }.9 : , ' [ | &. +.             ",
"      + ]@^@*@/@(@C+D+l+m+{+++@+#+]+^+8+n+o+p+E+F+V+-@;@_@:@<@[@}@|@1@~@{@$@%@R+q.i.j.8._.:.$.A }.9 : , ' [ | &. +.             ",
"      + 2@3@4@*@/@T+C+D+k+4+~+{+++#+]+^+7+8+n+o+U+F+V+W+5@6@:@7@8@9@1@~@{@$@%@R+q.i.j.8._.:.$.A }.9 : , ' [ | &. +.             ",
"      + 0@a@b@3@*@/@T+C+=@k+l+~+{+++5+]+6+7+8+n+o+U+E+F+V+-@6@7@8@9@1@~@c@$@d@R+z.i.B.8.e@:.~.A n 9 0 , ' [ | &.f@.             ",
"      + g@h@a@b@3@^@*@/@(@C+k+l+m+{+++@+#+6+7+8+n+o+p+E+F+V+-@i@8@9@j@~@c@$@d@R+z.i.B.8.e@:.~.A n 9 0 , ' [ | &.f@.             ",
"      + k@l@h@a@b@3@4@*@/@(@C+D+k+4+~+{+@+#+]+^+7+8+n+p+E+F+V+i@8@9@j@~@c@$@d@R+z.i.B.8.e@:.~.A n 9 0 , ' [ | &.f@.             ",
"      + m@n@o@p@h@a@3@4@*@/@T+C+=@k+4+~+{+++5+]+6+7+8+n+o+U+E+q@8@9@j@~@c@$@d@R+z.i.B.8.e@:.~.A n 9 0 , ' [ | &.r@.             ",
"      + s@t@n@u@l@h@a@b@3@^@*@/@C+=@k+l+m+{+++@+]+6+7+8+n+o+p+v@8@9@j@~@c@$@d@R+z.i.B.8.e@:.~.A n 9 0 , ' [ w@x@+ y@            ",
"      + z@A@B@n@u@l@h@a@b@3@^@*@/@(@C+D+k+4+{+++@+#+]+^+7+n+o+v@8@C@j@~@c@D@d@E@z.A.B.8.e@:.~.<.n 9 0 > F@G@# .                 ",
"      + z@A@A@B@H@n@o@p@h@b@3@4@*@/@T+C+D+k+4+~+{+++5+]+^+7+8+I@8@C@j@~@c@D@d@E@z.A.B.8.e@:.~.<.n 9 J@K@L@# +                   ",
"      + z@A@A@A@B@t@n@o@p@h@a@b@3@^@/@T+C+=@k+l+m+{+++5+]+6+7+I@8@C@j@~@c@D@d@E@z.A.B.8.e@:.~.<.M@N@O@+ @                       ",
"      + P@A@A@A@A@B@t@n@u@l@h@a@b@3@^@*@/@(@C+D+l+m+{+++@+#+]+I@8@C@j@~@c@D@d@E@z.A.B.8.e@:.~.Q@R@+ .                           ",
"      + @ S@T@U@A@A@A@B@H@n@o@h@a@b@3@4@*@/@T+C+D+k+4+~+{+++#+V@8@C@j@~@c@D@d@E@z.A.B.8.e@W@X@+ .                               ",
"        + @ + + Y@Z@`@ #B@H@n@o@p@h@a@b@3@*@/@T+C+=@k+l+~+{+++.#8@C@j@~@c@D@+#E@@#A.r.##$#5 .                                   ",
"                @ @ + %#&#*#=#n@u@l@h@a@b@3@^@*@/@(@C+k+l+m+{+-#8@C@j@~@c@D@+#E@@#;#>#U.@ +                                     ",
"                      + ,#+ '#)#!#~#l@h@a@b@3@4@*@/@(@C+D+k+4+{#8@C@j@~@c@D@+#E@]#^#+ ^                                         ",
"                            + ,#+ ,#/#(#_#h@a@3@4@*@/@T+C+=@k+:#8@C@j@~@c@D@<#[#+ .                                             ",
"                                  + @ + + }#|#1#2#3@^@*@/@C+=@3#8@C@j@~@4#5## .                                                 ",
"                                        + @ + + 6#7#8#9#*@/@(@0#8@a#b#c#d#@ +                                                   ",
"                                                + + + e#f#g#h#i#8@j#k#+ @                                                       ",
"                                                      + + + l#I.@ + .                                                           ",
"                                                            + + @ +                                                             ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                                                "};
                        """


'''
name1 = FreeCAD.ActiveDocument.addObject("App::FeaturePython","OriginalGeometry")
OriginalGeometry(name1)
name1.Label =  str(name1.OriginalObjectName)+'_'
ViewProviderDepthParams(name1.ViewObject)
App.activeDocument().recompute()
'''


import Draft

class _GeomBaseProxy(Draft._DraftObject):
    "Class representing proxy of Geometry"

    def __init__(self,obj,part):
        obj.setEditorMode('Placement',2)
        #obj.setEditorMode('Label',2)
        #obj.setEditorMode('Base',2)
        obj.addProperty("App::PropertyLink","Base","Geometry", "The base geometry this CAM featur is linked to")
        obj.Base = part
        Draft._DraftObject.__init__(self,obj,"DrillView")

    def execute(self,fp):
        pass

'''
sel=Gui.Selection.getSelection()
name = str(sel[0].Label)+"_proxy"
obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",name)
_GeomBaseProxy(obj, sel[0])
Draft._ViewProviderDraftAlt(obj.ViewObject)
App.activeDocument().recompute()
'''

class TypeOfOperation():
    def __init__(self,obj):
        obj.setEditorMode('Placement',2)
        obj.setEditorMode('Label',2)
        obj.addProperty("App::PropertyEnumeration", "AbsOrIncrMode", "Movement", "Abs/Incr Mode")
        obj.AbsOrIncrMode = ['Absolute','Incremental']
        obj.addProperty("App::PropertyEnumeration","TypeOfOperation","Machining","Machining Operation Type")
        obj.TypeOfOperation = ['Center_Drill', 'Drill', 'Peck_Drill', 'Profile', 'Pocket']
        obj.Proxy = self

    def execute(self,obj):
        pass

    def onChanged(self,obj,prop):
        App.activeDocument().recompute()

class ViewProviderTypeOfOperation:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


    def getIcon(self):
        return """
        /* XPM */
        static char * Machining_Parameters_xpm[] = {
        "16 16 22 1",
        " 	c None",
        ".	c #141010",
        "+	c #000000",
        "@	c #FFFFFF",
        "#	c #FBFBFB",
        "$	c #FDFDFD",
        "%	c #F5F5F5",
        "&	c #FEFEFE",
        "*	c #020202",
            "=	c #2F2F2F",
            "-	c #F9F9F9",
            ";	c #F1F1F1",
            ">	c #EFEFEF",
            ",	c #070707",
            "'	c #050505",
            ")	c #090909",
            "!	c #F8F8F8",
            "~	c #101010",
            "{	c #404040",
            "]	c #0C0C0C",
            "^	c #FEFDFE",
            "/	c #0A0808",
            "   ........+++  ",
            "   .@@@@@@#@@+  ",
            "   .@....@@@$+  ",
            "   .@@@@%@@&@.  ",
            "   .@...*+=$@.  ",
            "   .@@@@@@@-@.  ",
            "   .@....;;.@.  ",
            "   .@>%@@@@@@.  ",
            "   .@=,')+)@@.  ",
            "   .@!@@@@@@@)  ",
            "   .@)+~{%++@]  ",
            "   .@@@@@@@^@/  ",
            "   .@+'')@++@+  ",
            "   .@@@@@@@@@]  ",
            "   .@@@&&@@@@.  ",
            "   ...........  "};
                        """


'''
do = FreeCAD.ActiveDocument.addObject("App::FeaturePython","Operation Type")
TypeOfOperation(do)
ViewProviderTypeOfOperation(do.ViewObject)
App.activeDocument().recompute()
'''



class MovementObject():
    def __init__(self,obj):
        obj.addProperty("App::PropertyStringList","Movement","Base", "A list of feed or rapid moves")
        obj.Proxy = self
    def execute(self,obj):
        pass

class ViewProviderMovementObject:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def getIcon(self):
        return """
        /* XPM */
        static char * Parameters_xpm[] = {
        "16 16 22 1",
        "   c None",
        ".  c #141010",
        "+  c #000000",
        "@  c #FFFFFF",
        "#  c #FBFBFB",
        "$  c #FDFDFD",
        "%  c #F5F5F5",
        "&  c #FEFEFE",
        "*  c #020202",
            "=  c #2F2F2F",
            "-  c #F9F9F9",
            ";  c #F1F1F1",
            ">  c #EFEFEF",
            ",  c #070707",
            "'  c #050505",
            ")  c #090909",
            "!  c #F8F8F8",
            "~  c #101010",
            "{  c #404040",
            "]  c #0C0C0C",
            "^  c #FEFDFE",
            "/  c #0A0808",
           "   ........+++  ",
           "   .@@@@@@#@@+  ",
           "   .@....@@@$+  ",
           "   .@@@@%@@&@.  ",
           "   .@...*+=$@.  ",
           "   .@@@@@@@-@.  ",
           "   .@....;;.@.  ",
           "   .@>%@@@@@@.  ",
           "   .@=,')+)@@.  ",
           "   .@!@@@@@@@)  ",
           "   .@)+~{%++@]  ",
           "   .@@@@@@@^@/  ",
           "   .@+'')@++@+  ",
           "   .@@@@@@@@@]  ",
           "   .@@@&&@@@@.  ",
           "   ...........  "};
                       """
 
 
 
''' example useage:
# create one in the current doc
import toolpathparams
myobj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","toolpath")
toolpathparams.MovementObject(myobj)
toolpathparams.ViewProviderMovementObject(myobj.ViewObject)
# set some properties
myobj.Movement = ["G1X0Y0Z1.0","G1X1Z0F3.0"]
App.activeDocument().recompute()
'''
 


