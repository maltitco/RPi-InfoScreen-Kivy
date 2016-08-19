#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This is a custom layout for the RPi InfoScreen wordclock screen.

    Custom layouts can be created for the screen by creating a new file in the
    "layouts" folder.

    Each layout must have the following variables:
        LAYOUT:   The grid layout. Must be a single string.
        MAP:      The mapping required for various times (see notes below)
        COLS:     The number of columns required for the grid layout
        SIZE:     The size of the individual box containing your letter.
                  Tuple in (x, y) format.
        FONTSIZE: Font size for the letter
'''

# Layout is a single string variable which will be looped over by the parser.
LAYOUT = (u"JESTIZAMTRZYDZIEŚCI" # 18
          u"ODZIESIĘĆPIĘTNAŚCIE" # 37
          u"ADWDWADZIEŚCIAVPIĘĆ" # 56
          u"TRPOXPIĘTJEDENASTAS" # x - 75
          u"ÓSMADWUNASTACZWARTA" #76 - 94
          u"DRUGAPIĄTADPIERWSZA" # 95 -113
          u"SIÓDMATRZECIASZÓSTA" #x - 132
          u"DZIEWIĄTADZIESIĄTAR") # 133 - 151
# Map instructions:
# The clock works by rounding the time to the nearest 5 minutes.
# This means that you need to have settngs for each five minute interval "m00"
# "m00", "m05".
# The clock also works on a 12 hour basis rather than 24 hour:
# "h00", "h01" etc.
# There are three optional parameters:
#   "all": Anything that is always shown regardless of the time e.g. "It is..."
#   "am":  Wording/symbol to indicate morning.
#   "pm":  Wording/symbol to indicate afternoon/evening
MAP = {
       "all": [0, 1, 2, 3],
       "m00": [],
       "m05": [59, 60, 53, 54, 55, 56],
       "m10": [59, 60, 20, 21, 22, 23, 24, 25, 26, 27],
       "m15": [59, 60, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
       "m20": [59, 60, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
       "m25": [59, 60, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56],
       "m30": [59, 60, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
       "m35": [5, 6, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56],
       "m40": [5, 6, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
       "m45": [5, 6, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
       "m50": [5, 6, 20, 21, 22, 23, 24, 25, 26, 27],
       "m55": [5, 6, 53, 54, 55, 56],
       "h01": [106, 107, 108, 109, 110, 111, 112, 113],
       "h02": [95, 96, 97, 98, 99],
       "h03": [120, 121, 122, 123, 124, 125, 126],
       "h04": [87, 88, 89, 90, 91, 92, 93, 94],
       "h05": [100, 101, 102, 103, 104],
       "h06": [127, 128, 129, 130, 131, 132],
       "h07": [114, 115, 116, 117, 118, 119],
       "h08": [76, 77, 78, 79],
       "h09": [133, 134, 135, 136, 137, 138, 139, 140, 141],
       "h10": [142, 143, 144, 145, 146, 147, 148, 149, 150],
       "h11": [66, 67, 68, 69, 70, 71, 72, 73, 74],
       "h12": [80, 81, 82, 83, 84, 85, 86, 87],
       "am": [],
       "pm": []
  }

# Number of columns in grid layout
COLS = 19

# Size of letter in grid (x, y)
SIZE = (42, 60)

# Font size of letter
FONTSIZE = 40


# Is our language one where we need to increment the hour after 30 mins
# e.g. 9:40 is "Twenty to ten"
HOUR_INCREMENT = True
HOUR_INCREMENT_TIME = 30
