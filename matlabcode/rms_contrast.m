function rms = rms_contrast(img)
    img = double(img);
    mean_luminance = mean(img(:));
    rms = sqrt(mean((img(:) - mean_luminance).^2));
end