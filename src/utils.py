import numpy as np
import cv2


def sort_cw(pts):
    """Sort points clockwise by first splitting
    left/right points and then top/bottom.
    
    Acts on image coordinates, e.g. x-axis points
    rights and y-axis down.
    """
    pts = [list(p) for p in pts.reshape(-1, 2)]
    pts_sorted = sorted(pts , key=lambda k: k[0])
    pts_left = pts_sorted[:2]
    pts_right = pts_sorted[2:]
    pts_left_sorted = sorted(pts_left , key=lambda k: k[1])
    pts_right_sorted = sorted(pts_right , key=lambda k: k[1])
    tl = pts_left_sorted[0]
    bl = pts_left_sorted[1]
    tr = pts_right_sorted[0]
    br = pts_right_sorted[1]
    return np.array([tl, tr, br, bl])


def clip_to_image_region(quadrilateral, image_width, image_height):
    """Clips quadrilateral to image region.
    Note: Quadrilateral is modified in-place.
    """
    assert image_width > 0 and image_height > 0
    assert quadrilateral.shape == (4, 1, 2)
    quadrilateral[:, 0, 0] = np.clip(
        quadrilateral[:, 0, 0], 0, image_width - 1)
    quadrilateral[:, 0, 1] = np.clip(
        quadrilateral[:, 0, 1], 0, image_height - 1)
    return quadrilateral


def crop_module(frame, quadrilateral, crop_width=None, crop_aspect=None,
    rotate_mode="portrait"):
    """Crops out and rectifies image patch of single PV module in a given frame.

    Args:
        frame (`numpy.ndarray`): 1- or 3-channel frame (visual or IR) from which
            the module patch will be cropped out.

        quadrilaterals (`numpy.ndarray`): Shape (4, 1, 2). The four corner
            points of the module in the frame which were obtained by
            `find_enclosing_polygon` with `num_vertices = 4`.

        crop_width (`int`): If specified the resulting image patch will have
            this width. Its height is computed based on the provided value of
            `crop_aspect` as `crop_height = crop_width * crop_aspect`. If either
            `crop_width` or `crop_aspect` is set to `None` the width and height
            of the resulting patch correspdond to the maximum width and height
            of the module in the original frame.

        crop_aspect (`float`): The cropping aspect ratio.

        rotate_mode (`str` or `None`): If "portrait" ensures that module height
            is larger than module width by rotating modules with a wrong
            orientation. If "landscape" ensure width is larger than height. If
            `None` do not rotate modules with a potentially wrong orientation.

    Returns:
        Module patch (`numpy.ndarray`): The cropped and rectified patch of the
        module.

        Homography (`numpy.ndarray`): The homography which maps the
        quadrilateral onto a rectangular region.
    """
    assert frame.ndim == 2 or frame.ndim == 3
    assert quadrilateral.shape == (4, 1, 2)
    assert crop_width is None or crop_width > 0
    assert crop_aspect is None or crop_aspect > 0
    assert rotate_mode is None or rotate_mode in ["portrait", "landscape"]

    quadrilateral = clip_to_image_region(
        quadrilateral, frame.shape[1], frame.shape[0])
    tl, tr, br, bl = sort_cw(quadrilateral.reshape(-1, 2)).tolist()

    if crop_width is not None and crop_aspect is not None:
        crop_width = int(crop_width)
        crop_height = int(crop_width*crop_aspect)
    else:
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        crop_width = int(max(width_a, width_b))
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        crop_height = int(max(height_a, height_b))

    quadrilateral_sorted = np.array([[tl],[tr],[br],[bl]])
    dst_pts = np.array([[0., 0.],
                        [1., 0.],
                        [1., 1.],
                        [0., 1.]])
    dst_pts[:, 0] *= float(crop_width)
    dst_pts[:, 1] *= float(crop_height)
    homography = cv2.getPerspectiveTransform(
        quadrilateral_sorted.astype(np.float32), dst_pts.astype(np.float32))
    # note: setting border to "replicate" prevents insertion
    # of black pixels which screw up the range of image values
    module_patch = cv2.warpPerspective(
        frame, homography, dsize=(crop_width, crop_height),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if rotate_mode == "portrait":
        if module_patch.shape[0] < module_patch.shape[1]:
            module_patch = cv2.rotate(
                module_patch, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rotate_mode == "landscape":
        if module_patch.shape[1] < module_patch.shape[0]:
            module_patch = cv2.rotate(
                module_patch, cv2.ROTATE_90_COUNTERCLOCKWISE)

    return module_patch, homography