import plotly.graph_objects as go
import pandas as pd
import matplotlib.colors as mcolors
import numpy as np
import colorsys

FONT = 'Inter'


def generate_palette(hue, n_colors):
    saturation = 0.25
    lightness_start = 0.55
    lightness_end = 0.75
    lightness_range = np.linspace(lightness_start, lightness_end, n_colors)
    
    colors = []
    for lightness in lightness_range:
        s = saturation - (lightness - lightness_start) / (lightness_end - lightness_start) * 0.05
        rgb = colorsys.hls_to_rgb(hue, lightness, s)
        hex_color = mcolors.rgb2hex(rgb)
        colors.append(hex_color)
    
    return colors

bar_configs = [
    {
        'data': [
            {"generation": "USB 1.0", "mbs": 0.19},
            {"generation": "USB 1.1", "mbs": 1.5},
            {"generation": "USB 2.0", "mbs": 60},
            {"generation": "USB 3.0 / 3.1 Gen 1 / 3.2 Gen 1", "mbs": 625},
            {"generation": "USB 3.1 Gen 2 / 3.2 Gen 2", "mbs": 1250},
            {"generation": "USB 3.2 Gen 2×2", "mbs": 2500},
        ],
        'label': 'USB',
    },
    {
        'data': [
            {"generation": "HDD 5400 RPM", "mbs": 100},
            {"generation": "HDD 7200 RPM", "mbs": 180},
        ],
        'label': 'HDD',
    },
    {
        'data': [
            {"generation": "SD card (UHS-I)", "mbs": 90},
            {"generation": "SD card (UHS-II)", "mbs": 250},
        ],
        'label': 'SD Card',
    },
    {
        'data': [
            {"generation": "SSD (SATA)", "mbs": 550},
            {"generation": "SSD (NVMe PCIe 3.0)", "mbs": 3500},
            {"generation": "SSD (NVMe PCIe 4.0)", "mbs": 7000},
        ],
        'label': 'SSD',
    },
    {
        'data': [
            {"generation": "RAM (DDR1)", "mbs": 3000},
            {"generation": "RAM (DDR2)", "mbs": 6000},
            {"generation": "RAM (DDR3)", "mbs": 15000},
            {"generation": "RAM (DDR4)", "mbs": 25000},
            {"generation": "RAM (DDR5)", "mbs": 50000},
        ],
        'label': 'RAM',
        'visible': 'legendonly',
    },
    {
        'data': [
            {"generation": "L3 cache", "mbs": 100000},
            {"generation": "L2 cache", "mbs": 500000},
            {"generation": "L1 cache", "mbs": 1000000},
        ],
        'label': 'Cache',
        'visible': 'legendonly'
    },
    {
        'data': [
            {"generation": "Thunderbolt 1", "mbs": 1250},
            {"generation": "Thunderbolt 2", "mbs": 2500},
            {"generation": "Thunderbolt 3 / 4", "mbs": 5000},
        ],
        'label': 'Thunderbolt',
    },
    {
        'data': [
            {"generation": "Wi-Fi 4 (802.11n)", "mbs": 50},
            {"generation": "Wi-Fi 5 (802.11ac)", "mbs": 100},
            {"generation": "Wi-Fi 6 (802.11ax)", "mbs": 150},
            {"generation": "Wi-Fi 6E", "mbs": 200},
            {"generation": "Wi-Fi 7 (802.11be)", "mbs": 300},
        ],
        'label': 'Wi-Fi',
    },
    {
        'data': [
            {"generation": "Ethernet (100 MbE)", "mbs": 12},
            {"generation": "Ethernet (1 GbE)", "mbs": 125},
            {"generation": "Ethernet (2.5 GbE)", "mbs": 300},
            {"generation": "Ethernet (5 GbE)", "mbs": 600},
            {"generation": "Ethernet (10 GbE)", "mbs": 1250},
        ],
        'label': 'Ethernet',
    }
]

for config in bar_configs:
    config['df'] = pd.DataFrame(config['data'])
    config['max_speed'] = config['df']['mbs'].max()

bar_configs.sort(key=lambda x: x['max_speed'])

# Automatically assign hues evenly distributed across the spectrum
n_bars = len(bar_configs)
hues = np.linspace(0.0, 1.0, n_bars, endpoint=False)
for i, config in enumerate(bar_configs):
    config['hue'] = hues[i]
    n_colors = len(config['data'])
    config['colors'] = generate_palette(config['hue'], n_colors)


def add_stacked_bar(fig, labels, cumulative_values, x_label, colors, visible=True):
    cumulative_list = list(cumulative_values)
    incremental_values = [cumulative_list[0]] + [
        cumulative_list[i] - cumulative_list[i-1] 
        for i in range(1, len(cumulative_list))
    ]
    
    bottom = 0
    for i, (label, incremental_value, cum_value) in enumerate(zip(labels, incremental_values, cumulative_values)):
        text_color = 'white'
        cum_format = f'{cum_value:,.0f}'
        
        fig.add_trace(go.Bar(
            name=label,
            x=[x_label],
            y=[incremental_value],
            base=bottom,
            marker_color=colors[i],
            marker_line_color='white',
            marker_line_width=2,
            text=[f'<b>{label}<br>{cum_format} MB/s</b>'],
            textposition='inside',
            textfont=dict(
                size=12,
                color=text_color,
                family=FONT
            ),
            hovertemplate=f'<b>{label}</b><br>' +
                          f'Speed: {cum_format} MB/s<br>' +
                          '<extra></extra>',
            legendgroup=x_label,
            legendgrouptitle=dict(text=x_label),
            visible=visible
        ))
        bottom += incremental_value


fig = go.Figure()

for config in bar_configs:
    add_stacked_bar(
        fig=fig,
        labels=config['df']['generation'].values,
        cumulative_values=config['df']['mbs'].values,
        x_label=config['label'],
        colors=config['colors'],
        visible=config.get('visible', True)
    )

fig.update_layout(
    title={
        'text': 'Read/write speed comparison',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20, 'family': FONT}
    },
    yaxis=dict(
        title=dict(text='Speed (MB/s)', font=dict(size=14, family=FONT)),
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        tickformat=',.0f'
    ),
    xaxis=dict(
        title='',
        showgrid=False,
        tickfont=dict(size=12, family=FONT)
    ),
    barmode='stack',
    bargap=0,
    showlegend=True,
    legend=dict(
        orientation='v',
        yanchor='middle',
        y=0.5,
        xanchor='left',
        x=1.02,
        font=dict(size=10)
    ),
    plot_bgcolor='white',
    width=1280,
    height=720,
    margin=dict(l=80, r=200, t=80, b=50)
)

fig.write_html('index.html')
print("Interactive chart saved as 'index.html'")

fig.show()
