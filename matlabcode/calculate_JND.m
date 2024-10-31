function JND = calculate_JND(img)
    img = double(img) / 255;
    JND = mean(0.02 + 0.1 * sqrt(img(:)));
end