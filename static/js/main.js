document.addEventListener("DOMContentLoaded", function () {



    if (window.particlesJS) {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#00e1ff" },
                "shape": { "type": "circle" },
                "opacity": {
                    "value": 0.5,
                    "random": true,
                    "anim": { "enable": true, "speed": 1, "opacity_min": 0.1, "sync": false }
                },
                "size": {
                    "value": 3,
                    "random": true,
                    "anim": { "enable": true, "speed": 2, "size_min": 0.1, "sync": false }
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#00e1ff",
                    "opacity": 0.4,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1.5,
                    "direction": "none",
                    "random": true,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false,
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": { "enable": true, "mode": "grab" },
                    "onclick": { "enable": true, "mode": "push" },
                    "resize": true
                },
                "modes": {
                    "grab": { "distance": 140, "line_linked": { "opacity": 1 } },
                    "push": { "particles_nb": 4 }
                }
            },
            "retina_detect": true
        });
    }




    const chartElement = document.getElementById('failureChart');
    if (!chartElement) return;

    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            const ctx = chartElement.getContext('2d');
            

            const gradientSuccess = ctx.createLinearGradient(0, 0, 0, 400);
            gradientSuccess.addColorStop(0, 'rgba(57, 255, 20, 1)');
            gradientSuccess.addColorStop(1, 'rgba(57, 255, 20, 0.4)');

            const gradientFailed = ctx.createLinearGradient(0, 0, 0, 400);
            gradientFailed.addColorStop(0, 'rgba(255, 42, 42, 1)');
            gradientFailed.addColorStop(1, 'rgba(255, 42, 42, 0.4)');

            const gradientAborted = ctx.createLinearGradient(0, 0, 0, 400);
            gradientAborted.addColorStop(0, 'rgba(255, 145, 0, 1)');
            gradientAborted.addColorStop(1, 'rgba(255, 145, 0, 0.4)');


            const centerTextPlugin = {
                id: 'centerText',
                beforeDraw: function(chart) {
                    var width = chart.width,
                        height = chart.height,
                        ctx = chart.ctx;

                    ctx.restore();
                    var fontSize = (height / 120).toFixed(2);
                    ctx.font = "bold " + fontSize + "em Inter";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#ffffff";
                    ctx.shadowColor = "rgba(0, 225, 255, 0.5)";
                    ctx.shadowBlur = 10;

                    var text = data.total.toString(),
                        textX = Math.round((width - ctx.measureText(text).width) / 2),
                        textY = height / 2;

                    ctx.fillText(text, textX, textY);
                    
                    ctx.font = "normal " + (fontSize / 3) + "em Inter";
                    ctx.fillStyle = "#8b949e";
                    ctx.shadowBlur = 0;
                    var labelText = "Total Builds",
                        labelX = Math.round((width - ctx.measureText(labelText).width) / 2),
                        labelY = height / 2 + 30;
                    
                    ctx.fillText(labelText, labelX, labelY);
                    ctx.save();
                }
            };

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [gradientSuccess, gradientFailed, gradientAborted],
                        hoverBackgroundColor: ['#39ff14', '#ff2a2a', '#ff9100'],
                        borderColor: '#0a0b1a',
                        borderWidth: 5,
                        hoverOffset: 10,
                        hoverBorderColor: '#00e1ff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#e6edf3',
                                font: { family: "'Inter', sans-serif", size: 14, weight: '600' },
                                padding: 25,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(5, 5, 17, 0.9)',
                            titleColor: '#00e1ff',
                            bodyColor: '#e6edf3',
                            borderColor: 'rgba(0, 225, 255, 0.3)',
                            borderWidth: 1,
                            padding: 15,
                            displayColors: true,
                            boxPadding: 6,
                            cornerRadius: 8
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true,
                        duration: 1500,
                        easing: 'easeOutQuart'
                    }
                },
                plugins: [centerTextPlugin]
            });
        })
        .catch(error => console.error('Error fetching chart stats:', error));
});
