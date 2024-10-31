function michelson = michelson_contrast(img)
    Lmax = double(max(img(:)));
    Lmin = double(min(img(:)));
    michelson = (Lmax - Lmin) / (Lmax + Lmin);
end