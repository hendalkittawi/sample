"""
A GUI to generate canopy attributes from RGB and/or Multispectral Imagery.
Canpoy attributes generated: (vegitation indecies (VIs), canopy cover (cc), canopy height (ch), canopy volume (cv))
To generate ch and cv, the corresponding canopy height models (CHMs) should be available.
First generate .dat files that has the attributes values needed.
To store the attribute values in a shapefile, an EPSG value and initial shapefile with the field plots information should be provided.

* run in data_processing_gui environment
"""
import os
import glob
import tkinter as tk
from   tkinter            import *
from   tkinter.filedialog import askopenfilename, askdirectory
from   threading          import *
from   gen_dat_files      import get_dat_for_vi       # RGB VIs: exg, grvi, mgrvi, rgbvi, exgr
from   gen_vi_boundary    import get_boundary_for_vi  # MULTI VIs: ndvi, ndre, gndvi, savi, osavi, msavi, gci, reci, grvi
from   gen_ch_boundry     import get_ch_boundary
from   gen_cv_boundary    import get_cv_boundary

#TODO: add command for radio buttons to clear the lbl_msg values
#TODO: find a way to list all available EPSG values insted of only having the two we use

window = tk.Tk()

epsg_13                = 32613
epsg_14                = 32614
epsg_var               = tk.StringVar()

img_file               = tk.StringVar()
shp_file               = tk.StringVar()
results_dir            = tk.StringVar()
chm_dir                = tk.StringVar()

rd_btn_var             = tk.StringVar(value = "x")

rgb_vis                = ['exg', 'grvi', 'mgrvi', 'rgbvi', 'exgr', 'cc']
rgb_vi_chk_box_var     = [tk.IntVar() for i in range(len(rgb_vis) + 2)]

multi_vis              = ['ndvi', 'ndre', 'gndvi', 'savi', 'osavi', 'msavi', 'gci', 'reci', 'grvi']
multi_vi_chk_box_var   = [tk.IntVar() for i in range(len(multi_vis))]

files                  = []
chm_files              = []

widgets_width          = 25
widgets_height         = 3

def upload_img_threading():
    t1 = Thread(target = upload_img)
    t1.start()

def upload_shp_threading():
    t1 = Thread(target = upload_shp)
    t1.start()

def upload_chm_threading():
    t1 = Thread(target = upload_chm)
    t1.start()

def generate_results_threading():
    t1 = Thread(target = generate_results)
    t1.start()

def upload_img():
    print("Will upload the image")
    img_file.set(askopenfilename(filetypes=[("Image Files", "*.tif"), ("All Files", "*.*")]))

    if len(img_file.get()) == 0:
        print("Error reading the image file")
        return

    # load the image
    files.append(img_file.get())
    for f in files:
        print(f'Uploaded the image: {f}')

    # UI message
    img_filename = os.path.splitext(os.path.basename(img_file.get()))[0][:] # get filename without extension
    lbl_msg["text"] = f'Uploading the image \n {img_filename}'

    # UI message
    lbl_msg["text"] = 'Done uploading the image ...'

def delete_img():
    files.pop()
    print('Loaded images:')
    for f in files:
        print(f' \t\t{f}')

def select_out_folder():
    print("Will upload the image")
    results_dir.set(askdirectory())
    print(f'Will be saving the results to: {results_dir.get()}')

def upload_shp():
    print("Will upload the shp file")
    shp_file.set(askopenfilename(filetypes=[("All Files", "*.*")]))

    if len(shp_file.get()) == 0:
        print("Error reading the SHP file")
        lbl_msg["text"] = 'Error reading the SHP file'
        return

    # UI message
    shp_filename = os.path.splitext(os.path.basename(shp_file.get()))[0][:] # get filename without extension
    print(f'Uploaded the SHP file: {shp_filename}')
    lbl_msg["text"] = f'Uploaded the SHP file \n {shp_filename}'

def upload_chm():
    chm_dir.set(askdirectory())
    print(f'Selected the CHM folder as {chm_dir.get()}')

    chm_files = glob.glob(os.path.join(chm_dir.get(), '*.tif'))
    print(f'The files read are: {chm_files}')

    # add processing options related to CHM (ch and cv) to the processing list
    if len(chm_files) and rd_btn_var.get() == 'RGB':
        rgb_vis.append('ch')
        rgb_vis.append('cv')
        set_processing_options()

# create and set the values of check boxes
def set_processing_options():
    print('Will set processing options')

    # clear the chk_box_pannel options
    for widgets in chk_box_pannel.winfo_children():
        widgets.destroy()

    if rd_btn_var.get() == 'RGB':
        print('RGB options ...')

        # update the chk_box_pannel with rgb options
        for i in range(len(rgb_vis)):
            chk_box = tk.Checkbutton(chk_box_pannel, text = rgb_vis[i].upper(), variable = rgb_vi_chk_box_var[i])
            chk_box.grid(row = i + 1, column = 0, sticky = "w")

    if rd_btn_var.get() == 'MULTI':
        print('MULTI options ...')

        # update the chk_box_pannel with multi options
        for i in range(len(multi_vis)):
            chk_box = tk.Checkbutton(chk_box_pannel, text = multi_vis[i].upper(), variable = multi_vi_chk_box_var[i])
            chk_box.grid(row = i + 1, column = 0, sticky = "w")

def check_inputs(): #TODO : also check for the target options
    if(len(files) != 0 and len(results_dir.get()) != 0 and rd_btn_var.get() != 'x'):
        return True

    if(len(files) == 0 or len(results_dir.get()) == 0 or rd_btn_var.get() == 'x'):
        print(f'len(files) is {len(files)} \nlen(out_dir.get()) is {len(results_dir.get())} \nrd_btn_var is {rd_btn_var.get()}')
        lbl_msg["text"] = "Upload image(s) \nSelect output folder\nSelect image type\nSelect target outputs ..."
        return False

def check_optional_inputs():
    return

def generate_results():
    # TODO: check which boxes are checked
    #       for each checked box
    #          create output folder for dat files
    #          generate dat files
    #          check if shp file is Upload
    #              create folder for new shp file
    #              generate new shp file

    if not check_inputs():
        return

    print(f'img type is {rd_btn_var.get()}')

    # rgb processing
    if rd_btn_var.get() == 'RGB':
        vis_to_process = []
        for i in range(len(rgb_vis)):
            if rgb_vi_chk_box_var[i].get() != 0 and (rgb_vis[i] != 'ch' or rgb_vis[i] != 'cv'): #TODO: fix condition
                print (f'The option: {rgb_vis[i]} was set to: {rgb_vi_chk_box_var[i].get()}')
                vis_to_process.append(rgb_vis[i])
                print(f'RGB VIs to process {vis_to_process}')
            if rgb_vi_chk_box_var[i].get() != 0 and rgb_vis[i] == 'ch':
                print (f'The option: {rgb_vis[i]} was set to: {rgb_vi_chk_box_var[i].get()}')
                print('Will process canopy height ... ...')
                get_ch_boundary(epsg_val, shp_file.get(), chm_files, results_dir.get())
            if rgb_vi_chk_box_var[i].get() != 0 and rgb_vis[i] == 'cv':
                print (f'The option: {rgb_vis[i]} was set to: {rgb_vi_chk_box_var[i].get()}')
                print('Will process canopy volume ... ...')
                get_cv_boundary(epsg_val, shp_file.get(), chm_files, results_dir.get())

        get_dat_for_vi(files, results_dir.get(), rd_btn_var.get(), vis_to_process)
        print(f'Generated RGB dat files')
        lbl_msg["text"] = f'Generated RGB dat files'

    # multi processing
    if rd_btn_var.get() == 'MULTI':
        vis_to_process = []
        for i in range(len(multi_vis)):
            if multi_vi_chk_box_var[i].get() != 0:
                print (f'The option: {multi_vis[i]} was set to: {multi_vi_chk_box_var[i].get()}')
                vis_to_process.append(multi_vis[i])
        get_dat_for_vi(files, results_dir.get(), rd_btn_var.get(), vis_to_process)
        print(f'Generated MULTI dat files')
        lbl_msg["text"] = f'Generated MULTI dat files'

    if len(shp_file.get()) != 0:
        print(f'Will also process shapefile {shp_file.get()}')
        if epsg_var.get() == "13N":
            epsg_val = epsg_13
        elif epsg_var.get() == "14N":
            epsg_val = epsg_14
        else:
            lbl_msg["text"] = f'Set EPSG value'
            return

        # get_cc_boundary(epsg_val, shp_file.get(), results_dir.get())
        get_boundary_for_vi(epsg_val, shp_file.get(), results_dir.get(), vis_to_process)
        print(f'Generated shapefile(s)')
        lbl_msg["text"] = f'Generated shapefile(s)'

    lbl_msg["text"] = f'Done processing selected \noptions ...'


window.title("Data Processing GUI")
window.resizable(width = False, height = False)
window.rowconfigure(0, minsize = 500, weight = 1)
window.columnconfigure(1, minsize = 400, weight = 1)

#-------------------------------------------------------------------------------
# Widgets
#-------------------------------------------------------------------------------
header = tk.Label(text = "Data Processing GUI")

right_pannel = tk.Frame(
                    master = window,
                    bd     = 4
)

left_pannel = tk.Frame(
                    master = window,
                    relief = tk.RAISED,
                    bd     = 4
)

input_image_pannel = tk.Frame(
                    master = left_pannel,
                    bd     = 4
)

img_type_rd_btn_pannel = tk.Frame(
                    master = left_pannel,
                    bd     = 4
)

other_inputs_pannel = tk.Frame(
                    master = left_pannel,
                    bd     = 4
)

chk_box_pannel = tk.Frame(
                    master = right_pannel,
                    bd     = 4
)

btn_upload_img = tk.Button(
                    master = input_image_pannel,
                    text   = "Upload Field Image",
                    width = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command= upload_img_threading
)

btn_delete_img = tk.Button(
                    master = input_image_pannel,
                    text   = "Delete Uploaded Image",
                    width = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command= delete_img
)

btn_select_out_dir = tk.Button(
                    master = input_image_pannel,
                    text   = "Select Output Folder",
                    width = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command = select_out_folder
)

lbl_select_img_type = tk.Label(
                master = img_type_rd_btn_pannel,
                text   = "Select Image(s) Type",
                width  = widgets_width,
                height = widgets_height,
                bg     = "gainsboro",
                fg     = "black"
)

rd_btn_rgb = tk.Radiobutton(
               master = img_type_rd_btn_pannel,
               text = "RGB Image(s)",
               width  = widgets_width,
               height = 1,
               variable = rd_btn_var,
               value = 'RGB',
               command = set_processing_options)

rd_btn_multi = tk.Radiobutton(
               master = img_type_rd_btn_pannel,
               text = "MULTI Image(s)",
               width  = widgets_width,
               height = 1,
               variable = rd_btn_var,
               value = 'MULTI',
               command = set_processing_options)

lbl_attr_processing = tk.Label(
                master = other_inputs_pannel,
                text   = "----- Optional Inputs -----",
                width  = widgets_width,
                height = widgets_height,
                bg     = "gray99",
                fg     = "black"
)

btn_upload_shp = tk.Button(
                    master = other_inputs_pannel,
                    text   = "Upload Boundary File",
                    width = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command= upload_shp_threading
)

btn_upload_chm = tk.Button(
                    master = other_inputs_pannel,
                    text   = "Select CHM Folder",
                    width = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command= upload_chm_threading
)

txt_set_epsg = tk.Entry(
                master = other_inputs_pannel,
                width  = widgets_width,
                bg     = "dark sea green",
                fg     = "grey",
                justify = CENTER,
                textvariable = epsg_var)

lbl_select_outputs = tk.Label(
                master = right_pannel,
                text   = "----- Select Outputs -----",
                width  = widgets_width,
                height = widgets_height,
                bg     = "gray99",
                fg     = "black"
)

btn_gen_attributes = tk.Button(
                    master = right_pannel,
                    text   = "Generate Results",
                    width  = widgets_width,
                    height = widgets_height,
                    bg     = "gainsboro",
                    fg     = "black",
                    command = generate_results_threading
)

lbl_msg = tk.Label(
                master = right_pannel,
                text   = "Processing messages appear\n here",
                width  = widgets_width,
                height = 6,
                bg     = "gainsboro",
                fg     = "black",
)
#-------------------------------------------------------------------------------
# LAYOUT
#-------------------------------------------------------------------------------
# left pannel has the input_image_pannel, img_type_rd_btn_pannel, other_inputs_pannel
left_pannel.grid       (row=0, column=0, sticky="ns")

# left_pannel: input_img_pannel: upload image, delete image, select output directory
input_image_pannel.grid(row=1, column=0, sticky="ew", pady=5)
btn_upload_img.grid    (row=0, column=0, sticky="ew")
btn_delete_img.grid    (row=1, column=0, sticky="ew")
btn_select_out_dir.grid(row=2, column=0, sticky="ew")

# left_pannel: other_inputs_pannel: upload shapefile, upload chm, upload epsg
other_inputs_pannel.grid(row=2, column=0, sticky="ew", pady=5)
lbl_attr_processing.grid(row=0, column=0, sticky="ew")
btn_upload_shp.grid     (row=1, column=0, sticky="ew")
btn_upload_chm.grid     (row=2, column=0, sticky="ew")
txt_set_epsg.grid       (row=3, column=0, sticky="ew")

# left_pannel: img_type_rd_btn_pannel: select image type radio buttons
img_type_rd_btn_pannel.grid (row=3, column=0, sticky="ew", pady=5)
lbl_select_img_type.grid    (row=0, column=0, sticky="ew")
rd_btn_rgb.grid             (row=1, column=0, sticky="ew")
rd_btn_multi.grid           (row=2, column=0, sticky="ew")

# right pannel has the lbl_select_outputs, chk_box_pannel, btn_gen_attributes, lbl_msg
right_pannel.grid       (row=0, column=1, sticky="ew", padx=5)
lbl_select_outputs.grid (row=0, column=0, sticky="ew")
chk_box_pannel.grid     (row=1, column=0, sticky="ew")
btn_gen_attributes.grid (row=2, column=0, sticky="ew")
lbl_msg.grid            (row=3, column=0, sticky="ew", pady=50)

txt_set_epsg.insert(INSERT, "Set EPSG 13N for Amarillo 14N Else")
rd_btn_rgb.deselect()
rd_btn_multi.deselect()

window.mainloop()
