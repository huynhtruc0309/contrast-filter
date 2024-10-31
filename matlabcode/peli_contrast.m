function peli = peli_contrast(img)
    img = double(img);
    sigma = 1.5;
    lowpass = imgaussfilt(img, sigma * 2);
    bandpass = img - lowpass;
    epsilon = 1e-5;
    contrast_map = bandpass ./ (lowpass + epsilon);
    contrast_map(lowpass < epsilon) = 0;
    peli = mean(abs(contrast_map(:)));
end
