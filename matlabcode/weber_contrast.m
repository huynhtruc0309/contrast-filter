function weber = weber_contrast(img)
    Lmax = double(max(img(:)));
    Lmin = double(min(img(:)));
    weber = (Lmax - Lmin) / Lmin;
end