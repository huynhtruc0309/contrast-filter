function mean_diff = local_mean_diff(img)
    window_size = 3;
    mean_filter = fspecial('average', [window_size window_size]);
    local_mean = imfilter(double(img), mean_filter, 'replicate');
    mean_diff = std(double(img(:)) - local_mean(:));
end