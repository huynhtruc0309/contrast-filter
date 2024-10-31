function ratio = max_min_ratio(img)
    Lmax = double(max(img(:)));
    Lmin = double(min(img(:)));
    ratio = Lmax / Lmin;
end