function plot_CSF_comparison(img1, img2)
    f = linspace(0.1, 60, 500);
    a = 75; b = 0.2; c = 0.8;
    CSF1 = a * (f .^ c) .* exp(-b * f);
    CSF2 = a * (f .^ c) .* exp(-b * f);
    figure;
    plot(f, CSF1, 'b-', 'LineWidth', 2);
    hold on;
    plot(f, CSF2, 'r-', 'LineWidth', 2);
    xlabel('Spatial Frequency (cycles/degree)');
    ylabel('Sensitivity');
    title('Contrast Sensitivity Function (CSF) Comparison');
    legend('Original Image', 'Filtered Image');
    grid on;
end