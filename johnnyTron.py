# Created on Tues Aug 2 9:11:16 2022

# Author: John Gumm

# Massachusetts Institute of Technology
# Research Laboratory of Electronics
# Quantum Nanostructures and Nanofabrication

from phidl import Device
import phidl.geometry as pg
import phidl.routing as pr
import myOwnDesign as md

# Sizing variables
workspace_length, workspace_height, pad_size, feature_size = 5000, 5000, 450, 2

# Layer variables
die_layer = pad_layer = snspd_layer = star_layer = rect_layer = txt_layer = image_layer = 0

# Add die template
D = Device('johnnytron')
D << pg.basic_die(size = (workspace_length, workspace_height), street_width = 75, street_length = 1000,
                die_name = 'John Gumm' + (' ' * 19) + 'QNN Aug 2022', text_size = 120, 
                text_location = 'SW', layer = die_layer, draw_bbox = False, bbox_layer = 99)

# Pad/Connectors loop
pads = [pg.compass()]
for i in range(1, 11):
    if(i < 6):
        # Left pads
        pads.append(D << pg.compass((pad_size, pad_size), pad_layer))
        pads[i].movex(-2000).movey(-1900 + 500 * i)
    else:
        # Bottom pads
        pads.append(D << pg.compass((pad_size, pad_size), pad_layer))
        pads[i].movex(-2000 + 500 * (i-5)).movey(-1900)

        # Add connectors between pads
        D << pr.route_sharp(
        port1 = pads[i].ports['N'], port2 = pads[i-5].ports['E'], width = ((30/(i-5))), 
        path_type = 'Z', manual_path = None, layer = pad_layer)

# Star loop
for i in range(4, 7):
    D << pg.litho_star(i * 4, feature_size * 3, 100 * i, star_layer).movex(2000).movey(700*i - 2300)

# Line loop
for i in range (1, 50):
    if(i < 40 or i == 49):
        D << pg.rectangle((i + 1, 1000), rect_layer).movex(-2200 + i * feature_size * 38).movey(1200)
    else:
        D << pg.rectangle((i + 1, 50), rect_layer).movex(-2200 + i * feature_size * 38).movey(1200)
        D << pg.rectangle((i + 1, 50), rect_layer).movex(-2200 + i * feature_size * 38).movey(2150)

# SNSPD pad array
snspd_pads_top, snspd_pads_bottom, snspd_contact_pads, snspd = [], [], [], []

for i in range(0, 6):
    snspd_pads_top.append(D << pg.compass((pad_size, pad_size), pad_layer).movex(1350 - (i * 500)).movey(900))
    snspd_pads_bottom.append(D << pg.compass((45, 45), pad_layer).movex((1650 - (i * 500))/4).movey(200))
    D << pr.route_sharp(
        port1 = snspd_pads_top[i].ports['S'], port2 = snspd_pads_bottom[i].ports['N'], width = (25),
        path_type = 'Z', manual_path = None, layer = pad_layer)
    snspd.append(D << pg.snspd_expanded(feature_size * 2, feature_size * 6, 
                        (100, 1500 - (i * 250)), terminals_same_side= True, connector_width=4))
    snspd_contact_pads.append(D << pg.compass((4,4), pad_layer))
    snspd[i].movex((1350 - (i * 500))/2)
    snspd_contact_pads[i].move(snspd_contact_pads[i].ports['W'], snspd[i].ports[1])
    D << pr.route_quad(snspd_pads_bottom[i].ports['S'], snspd_contact_pads[i].ports['N'], 4, 4)
    if((i % 2) != 0):
        D << pr.route_quad(snspd[i-1].ports[2], snspd[i].ports[2], 8, 8)

class EmptyClass:
    pass

# Pixel Parameters 
imagecell = EmptyClass()
imagecell.pixel = 6                  # the size of our pixels.  Keep at 30 um or larger
imagecell.pixelspacing = 2.0         # small gap between pixels to avoid litho errors. keep at 2.0
imagecell.minsize = 4                # min length of the pixel. keep at 4.0 or larger
imagecell.framewidth= 100            # frame to draw around image, makes it easier to recignize
imagecell.framespace = 20
imagecell.grating = EmptyClass()     # pixels can be squares or gratings
imagecell.grating.pitch = 8          # with wet etching, advise not to use gratings
imagecell.grating.width = 6
imagecell.grating.omit = True        # gratings? T of F. for our process, better to omit
imagecell.maxwidth  = 850            # image will be rescaled to fit this box
imagecell.maxheight = 850
imagecell.layer = image_layer

# Draw Nic Cage
D << md.drawImage(imagecell,md.Image.open('nic_cage.jpg').convert('L')).move((1165,1701))

# Write text
text_file = open('johnnytron.py', 'r')
text_data = text_file.read()
D << pg.text(text_data, size = 18, layer = txt_layer).movex(900).movey(335)

# Write to gds
D.write_gds('johnnytron.gds', auto_rename=True)
