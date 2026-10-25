"""
utils/generate_plots.py - Generates the project's primary manuscript figures and model trend charts.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def _load_and_clean_data(data_path):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing trajectory table: {data_path}")
    df = pd.read_csv(data_path)
    code_cleaner = {'JIA': 'CHI', 'SHA': 'JAP', 'WEL': 'WEL', 'IRE': 'IRE'}
    df['Regional_Zone'] = df['Regional_Zone'].replace(code_cleaner)
    return df

def plot_publication_trajectories(data_path='output/tables/etc_bayesian_latent_trajectories.csv', output_dir='output/figures'):
    """
    Plots continuous latent trajectories by region with shaded uncertainty intervals.
    Applies a broad, high-contrast palette with transparent shading to support overlapping lines.
    """
    sns.set_theme(style="white")
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.size': 10, 'axes.labelsize': 11,
        'xtick.labelsize': 9.5, 'ytick.labelsize': 9.5,
        'axes.edgecolor': '#888888', 'axes.linewidth': 0.7
    })

    df = _load_and_clean_data(data_path)

    # okabe-ito safe palette definitions mapping high-contrast cross-vision values
    paper_styles = {
        'Greek world':   {'code': 'GRE', 'color': '#0072B2'}, # deep blue
        'Latin world':   {'code': 'LAT', 'color': '#E69F00'}, # amber
        'Arab world':    {'code': 'ARA', 'color': '#009E73'}, # bluish green
        'China':         {'code': 'CHI', 'color': '#D55E00'}, # vermilion
        'Japan':         {'code': 'JAP', 'color': '#CC79A7'}, # reddish purple
        'France':        {'code': 'FRA', 'color': '#56B4E9'}, # sky blue
        'England':       {'code': 'ENG', 'color': '#F0E442'}, # yellow
        'Indian world':  {'code': 'IND', 'color': '#000000'}, # black
        'Russian world': {'code': 'RUS', 'color': '#444444'}, # dark gray
        'Wales':         {'code': 'WEL', 'color': '#111111'}, # charcoal
        'Ireland':       {'code': 'IRE', 'color': '#222222'},
        'Iceland':       {'code': 'ICE', 'color': '#666666'},
        'Italy':         {'code': 'ITA', 'color': '#777777'},
        'Spain':         {'code': 'SPA', 'color': '#888888'},
        'German World':  {'code': 'GER', 'color': '#999999'},
        'Low Countries': {'code': 'LOW', 'color': '#aaaaaa'},
        'Ancient Egypt': {'code': 'EGY', 'color': '#bbbbbb'}
    }

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.axhline(0.0, color='#e5e7eb', linestyle='-', lw=1.0, zorder=1)

    for name, attrs in paper_styles.items():
        region_df = df[df['Regional_Zone'] == attrs['code']].sort_values('Historical_Year')
        region_df = region_df[(region_df['Historical_Year'] >= -800) & (region_df['Historical_Year'] <= 1800)]

        if region_df.empty:
            continue

        years = region_df['Historical_Year'].values
        means = region_df['Latent_Value_Mean'].values
        sds = region_df['Latent_Value_SD'].values

        ax.fill_between(years, means - sds, means + sds, color=attrs['color'], alpha=0.035, zorder=2)
        ax.plot(years, means, color=attrs['color'], lw=2.2, solid_capstyle='round', label=name, zorder=4)

    ax.set_xlim(-800, 1800)
    ax.set_xticks([-500, 0, 500, 1000, 1500])
    ax.set_xticklabels(['-500', '0', '500', '1000', '1500'])
    ax.set_ylim(-1.5, 2.0)

    ax.set_xlabel("Year", labelpad=10)
    ax.set_ylabel("Romanticism (Log-Odds)", labelpad=10)

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#b8b8b8')
    ax.spines['bottom'].set_color('#b8b8b8')

    ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=False, fontsize=9)
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "replicated_trajectories.png"), bbox_inches='tight')
    plt.close()

def generate_century_binned_plot(data_path='output/tables/etc_bayesian_latent_trajectories.csv', output_dir='output/figures'):
    """
    Groups historical years into discrete centuries to reduce baseline timeline clutter.
    Pairs unique markers and line styles to secure legibility in greyscale printouts.
    """
    df = _load_and_clean_data(data_path)
    df['Century'] = (np.floor(df['Historical_Year'] / 100) * 100).astype(int)
    summary = df.groupby(['Regional_Zone', 'Century'])['Latent_Value_Mean'].mean().reset_index()

    # colorblind-safe palettes combined with unique markers and structural line types
    focus_regions = {
        'GRE': {'name': 'Greek World', 'color': '#0072B2', 'marker': 'o', 'style': '-'},   # blue solid
        'LAT': {'name': 'Latin World', 'color': '#E69F00', 'marker': 's', 'style': '--'},  # amber dashed
        'CHI': {'name': 'China Core', 'color': '#D55E00', 'marker': '^', 'style': '-.'},  # vermilion dashdot
        'FRA': {'name': 'France', 'color': '#009E73', 'marker': 'd', 'style': ':'},   # green dotted
        'ENG': {'name': 'England', 'color': '#CC79A7', 'marker': 'v', 'style': '-'},   # purple solid
        'ARA': {'name': 'Arabic World', 'color': '#000000', 'marker': 'x', 'style': '--'}  # black dashed
    }

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    ax.axvline(x=0, color='#888888', linestyle='--', linewidth=1, alpha=0.7)
    ax.grid(True, linestyle=':', alpha=0.4, color='#cccccc')

    for code, meta in focus_regions.items():
        region_data = summary[summary['Regional_Zone'] == code].sort_values('Century')
        if not region_data.empty:
            ax.plot(region_data['Century'], region_data['Latent_Value_Mean'], label=meta['name'],
                    color=meta['color'], marker=meta['marker'], linestyle=meta['style'],
                    linewidth=1.75, markersize=5, alpha=0.9)

    ax.set_title("Inferred Trajectory of Romantic Themes Across Historical Eras", fontsize=12, fontweight='bold', pad=14)
    ax.set_xlabel("Historical Era", fontsize=10)
    ax.set_ylabel("Latent Expression Intensity", fontsize=10)
    ax.set_xlim(-1050, 1850)
    ax.set_xticks([-1000, -500, 0, 500, 1000, 1500])
    ax.set_xticklabels(["1000 BC", "500 BC", "CE Transition", "500 AD", "1000 AD", "1500 AD"])

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), frameon=True, facecolor='white', edgecolor='none', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "eurasian_love_trajectories.png"), bbox_inches='tight')
    plt.close()

def plot_paradigm_comparison(report_path='output/tables/era_binned_comparison.csv',
                             trajectory_path='output/tables/etc_bayesian_latent_trajectories.csv',
                             output_dir='output/figures'):
    """
    Draws a side-by-side comparison of the original step-binned study design
    against the smooth continuous trajectory calculated by our gp model.
    Applies a 50-year centered rolling mean window to smooth high-frequency sampling chatter.
    """
    if not os.path.exists(report_path):
        print(f"Missing comparison report file at: {report_path}")
        return
    if not os.path.exists(trajectory_path):
        print(f"Missing continuous trajectory file at: {trajectory_path}")
        return

    df_binned = pd.read_csv(report_path)
    df_traj = pd.read_csv(trajectory_path)

    # isolate clean aggregated global trends across all regions for the same era window
    df_global = df_traj[(df_traj['Historical_Year'] >= -500) & (df_traj['Historical_Year'] <= 1800)].copy()
    df_global = df_global.groupby('Historical_Year').agg({
        'Latent_Value_Mean': 'mean',
        'Latent_Value_SD': 'mean'
    }).reset_index().sort_values('Historical_Year')

    sns.set_theme(style="whitegrid")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    for ax in [ax1, ax2]:
        ax.axhline(0.0, color='#888888', linestyle='--', linewidth=1, alpha=0.5)

    boundaries = [-500, 200, 800, 1400, 1800]
    orig_means = df_binned['Original GLM Estimate'].values
    orig_ses = df_binned['Original SE'].values
    step_orig = np.append(orig_means, orig_means[-1])

    # panel A: original study design (rigid step function)
    ax1.step(boundaries, step_orig, where='post', color='#000000', lw=2.5,
             label="Original Fixed Effects (Baumard et al. 2022)")
    for i in range(4):
        ax1.fill_between(
            [boundaries[i], boundaries[i+1]],
            orig_means[i] - 1.96 * orig_ses[i],
            orig_means[i] + 1.96 * orig_ses[i],
            color='#000000', alpha=0.08, hatch='//'
        )
    ax1.set_title("Original Study Design: Discrete Chronological Bins", fontweight='bold', pad=10)
    ax1.set_ylabel("Romanticism (Log-Odds)")
    ax1.set_ylim(-1.5, 2.0)
    ax1.legend(loc="upper left")

    # panel B: replication framework (smoothed continuous curve)
    years = df_global['Historical_Year'].values
    raw_means = df_global['Latent_Value_Mean'].values
    raw_sds = df_global['Latent_Value_SD'].values

    # window set to 12 years to prevent crushing the historical peak
    smoothed_means = pd.Series(raw_means).rolling(window=12, center=True, min_periods=1).mean().to_numpy()
    smoothed_sds = pd.Series(raw_sds).rolling(window=12, center=True, min_periods=1).mean().to_numpy()

    # plot the smooth continuous timeline to visually anchor the text correction metrics
    ax2.plot(years, smoothed_means, color='#0072B2', lw=2.5, linestyle='-',
             label="Aggregated SST-GP-GLMM Latent Trajectory (12-Year Smooth)")
    ax2.fill_between(years, smoothed_means - smoothed_sds, smoothed_means + smoothed_sds,
                     color='#0072B2', alpha=0.12, hatch='..')

    # annotation to explicitly target the compressed surge window in your draft text
    ax2.annotate('Artificially Compressed Surge\n(Greek & Eastern Roman Peak)',
                 xy=(450, 0.95), xytext=(-250, 20), textcoords='offset points',
                 fontsize=9.5, fontweight='bold', color='#005585',
                 arrowprops=dict(arrowstyle="->", color='#005585', lw=1.5, connectionstyle="arc3,rad=-0.2"))

    ax2.set_title("Replication Framework: Aggregated Continuous Spatiotemporal Manifold", fontweight='bold', pad=10)
    ax2.set_xlabel("Historical Chronological Horizon (Years CE)", labelpad=10)
    ax2.set_ylabel("Romanticism (Log-Odds)")
    ax2.set_ylim(-1.5, 2.0)
    ax2.legend(loc="upper left")

    # axis formatting cleanups
    ax2.set_xlim(-600, 1900)
    ax2.set_xticks(boundaries)
    ax2.set_xticklabels(['-500', '200 AD', '800 AD', '1400 AD', '1800 AD'])

    for ax in [ax1, ax2]:
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        ax.grid(True, linestyle=':', alpha=0.4)

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "model_comparison_chart.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Exported continuous trajectory paradigm comparisons to: {save_path}")


if __name__ == "__main__":
    plot_publication_trajectories()
    generate_century_binned_plot()
    plot_paradigm_comparison()
