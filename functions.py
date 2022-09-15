import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from string import ascii_uppercase
import re

def get_masks(CellMask_path, thickness=7):
    """
    Using the CellMask image path as input, get 2 new masks as output:
     1 - cell contours (membrane)
     2 - cell without contours (without membrane)
     the function filters out objects that are not round to remove objects that were segmented poorly
      * thickness parameter will define the thickness of the contour
      * if no cells found in the mask - return 'None', 'None'
     """
    CellMask = cv2.imread(CellMask_path, cv2.IMREAD_GRAYSCALE)  # read image in greyscale (one channel image)
    # image binarization with 'Otsu Threshold'
    _, CellMask_bin = cv2.threshold(CellMask, 0, 1, cv2.THRESH_OTSU)
    # find objects contours
    contours_candidates, _ = cv2.findContours(CellMask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # filter for only circular contours
    contours = []
    for c in contours_candidates:
        # calculate R from 2 sources
        perimeter = cv2.arcLength(c, True)  # perimeter of circle = 2 * pi * radius
        area = cv2.contourArea(c)  # area of circle = pi * radius ** 2
        if perimeter != 0:
            circularity = 4 * np.pi * (area / (perimeter ** 2))  # circularity = ... = (R calc from area)^2 / (R calc from perimeter)^2
            if 0.6 < circularity < 1.4:  # circularity == 1 -> perfect circle
                contours.append(c)

    # draw contours to create the new masks:
    # for mask 1 - only contours (cell membrane):
    contours_mask = np.zeros(CellMask_bin.shape, dtype=np.uint8)
    cv2.drawContours(contours_mask, contours, -1, 1, thickness=thickness)
    # for mask 2 - without contours:
    filled_contours_mask = np.zeros(CellMask_bin.shape, dtype=np.uint8)
    cv2.drawContours(filled_contours_mask, contours, -1, 1, thickness=cv2.FILLED)
    # remove contours from filled_contours_mask
    # invert contours mask
    _, inv_contours_mask = cv2.threshold(contours_mask, 0, 1, cv2.THRESH_BINARY_INV)
    in_contours_mask = cv2.bitwise_and(filled_contours_mask, filled_contours_mask, mask=inv_contours_mask)
    return contours_mask, in_contours_mask


def Quantification(contours_mask, in_contours_mask, img_path):
    """
    This function get 3 params as input:
     - contours_mask: mask segmenting only the cell membrane (conture)
     - in_contours_mask: mask segmenting only the inside of the cell, without membrane (conture)
     - img_path: path to the image to be quantified
     - pixel_size: conversion factor (um/pixel)
     This function returns:
     - df: Dataframe containing Area (number of pixels), Total intensity, and Mean intensity for cell membrane
           and for cell without membrane
           The index in the dataframe represents the well ID and position ('A1-1' -> well A1, position 1)
    """
    # load image to be quantified (img_path)
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    # overlay masks with img
    img_contours = cv2.bitwise_and(img, img, mask=contours_mask)
    img_in_contours = cv2.bitwise_and(img, img, mask=in_contours_mask)

    # calculate results and create df to return:
    df = pd.DataFrame({
        "Well ID": img_path.split('--')[0][-2:],
        'Well Number': str(int(img_path.split('--')[1][1:])),
        "Position": str(int(img_path.split('--')[2][1:])),
        "Membrane Area (# pixels)": np.count_nonzero(img_contours),
        "Membrane Total intensity": img_contours.sum(),
        "Membrane Mean intensity": img_contours[np.nonzero(contours_mask)].mean(),
        "W_O Membrane Area (# pixels)": np.count_nonzero(img_in_contours),
        "W_O Membrane Total intensity": img_in_contours.sum(),
        "W_O Membrane Mean intensity": img_in_contours[np.nonzero(in_contours_mask)].mean()
    }, index=[img_path.split('--')[0][-2:] + ' - ' + str(int(img_path.split('--')[2][1:]))])
    return df


def conv_wellID_num(pre_conv, plate_shape, method):
    """
    This function convert from Well ID to Well number and vice versa in 2 methods row stack and column stack
    inputs:
     - pre_conv: strings or integers to be converted
     - plate_shape: shape of plate (list of 2 integers). for standard 384 well plate - plate_shape = [16,24]
     - method: 4 options - 'ID2num_row_stack', 'ID2num_column_stack', 'num2ID_row_stack', 'num2ID_column_stack'
    return:
     - post_conv: converted string
    """
    if method == 'ID2num_row_stack':
        row, col, _ = re.split(r'(\d+)', pre_conv)
        post_conv = ascii_uppercase.index(row) * plate_shape[1] + int(col)
    elif method == 'ID2num_column_stack':
        row, col, _ = re.split(r'(\d+)', pre_conv)
        post_conv = ascii_uppercase.index(row) + 1 + plate_shape[0] * (int(col) - 1)
    elif method == 'num2ID_row_stack':
        row = int(pre_conv) // plate_shape[1]
        col = int(pre_conv) % plate_shape[1]
        if col == 0:
            col = plate_shape[1]
            row -= 1
        post_conv = ascii_uppercase[row] + str(col)
    elif method == 'num2ID_column_stack':
        row = int(pre_conv) % plate_shape[0]
        col = int(pre_conv) // plate_shape[0] + 1
        if row == 0:
            row = plate_shape[0]
            col -= 1
        post_conv = ascii_uppercase[row - 1] + str(col)

    return post_conv











