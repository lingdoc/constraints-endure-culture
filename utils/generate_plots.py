"""
Generates the project's primary manuscript figures and model trend charts.
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
    """
    sns.set_theme(style="white")
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.size': 10, 'axes.labelsize': 11,
        'xtick.labelsize': 9.5, 'ytick.labelsize': 9.5,
        'axes.edgecolor': '#888888', 'axes.linewidth': 0.7
    })

    df = _load_and_clean_data(data_path)

    paper_styles = {
        'Greek world':   {'code': 'GRE', 'color': '#0B132B'},
        'Latin world':   {'code': 'LAT', 'color': '#1C2541'},
        'Arab world':    {'code': 'ARA', 'color': '#007F5F'},
        'China':         {'code': 'CHI', 'color': '#D94E34'},
        'Japan':         {'code': 'JAP', 'color': '#E9C46A'},
        'France':        {'code': 'FRA', 'color': '#00B4D8'},
        'England':       {'code': 'ENG', 'color': '#0077B6'},
        'Indian world':  {'code': 'IND', 'color': '#9B2226'},
        'Russian world': {'code': 'RUS', 'color': '#7209B7'},
        'Wales':         {'code': 'WEL', 'color': '#4CC9F0'},
        'Ireland':       {'code': 'IRE', 'color': '#B5179E'},
        'Iceland':       {'code': 'ICE', 'color': '#F72585'},
        'Italy':         {'code': 'ITA', 'color': '#4a5759'},
        'Spain':         {'code': 'SPA', 'color': '#2f3e46'},
        'German World':  {'code': 'GER', 'color': '#6b705c'},
        'Low Countries': {'code': 'LOW', 'color': '#a5a58d'},
        'Ancient Egypt': {'code': 'EGY', 'color': '#3f37c9'}
    }

    fig, ax = plt.subplots(figsize=(10.5, 7.5), dpi=300)
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
    """
    df = _load_and_clean_data(data_path)
    df['Century'] = (np.floor(df['Historical_Year'] / 100) * 100).astype(int)
    summary = df.groupby(['Regional_Zone', 'Century'])['Latent_Value_Mean'].mean().reset_index()

    focus_regions = {
        'GRE': {'name': 'Greek World', 'color': '#1f77b4', 'marker': 'o'},
        'LAT': {'name': 'Latin World', 'color': '#7bc8f6', 'marker': 's'},
        'CHI': {'name': 'China Core', 'color': '#ff7f0e', 'marker': '^'},
        'FRA': {'name': 'France', 'color': '#d62728', 'marker': 'd'},
        'ENG': {'name': 'England', 'color': '#9467bd', 'marker': 'v'},
        'ARA': {'name': 'Arabic World', 'color': '#2ca02c', 'marker': 'x'}
    }

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axvline(x=0, color='#888888', linestyle='--', linewidth=1, alpha=0.7)
    ax.grid(True, linestyle=':', alpha=0.4, color='#cccccc')

    for code, meta in focus_regions.items():
        region_data = summary[summary['Regional_Zone'] == code].sort_values('Century')
        if not region_data.empty:
            ax.plot(region_data['Century'], region_data['Latent_Value_Mean'], label=meta['name'],
                    color=meta['color'], marker=meta['marker'], linewidth=1.75, markersize=5, alpha=0.9)

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

def plot_paradigm_comparison(report_path='output/tables/era_binned_comparison.csv', output_dir='output/figures'):
    """
    Draws a side-by-side comparison of the original step-binned study against our model.
    """
    if not os.path.exists(report_path):
        print(f"[WARNING] Missing comparison report file at: {report_path}")
        return

    df = pd.read_csv(report_path)
    sns.set_theme(style="whitegrid")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    for ax in [ax1, ax2]:
        ax.axhline(0.0, color='#888888', linestyle='--', linewidth=1, alpha=0.5)

    boundaries = [-500, 200, 800, 1400, 1800]
    
    orig_means = df['Original GLM Estimate'].values
    orig_ses = df['Original SE'].values
    bayes_means = df['Your Bayesian Mean'].values
    bayes_sds = df['Your Cross-Regional SD'].values

    step_orig = np.append(orig_means, orig_means[-1])
    step_bayes = np.append(bayes_means, bayes_means[-1])

    # original paper data
    ax1.step(boundaries, step_orig, where='post', color='#b21f2d', lw=2.5, label="Original Fixed Effects (Baumard et al. 2022)")
    for i in range(4):
        ax1.fill_between(
            [boundaries[i], boundaries[i+1]],
            orig_means[i] - 1.96 * orig_ses[i],
            orig_means[i] + 1.96 * orig_ses[i],
            color='#b21f2d', alpha=0.1
        )
    ax1.set_title("Original Study Design: Discrete Chronological Bins", fontweight='bold', pad=10)
    ax1.set_ylabel("Romanticism (Log-Odds)")
    ax1.set_ylim(-1.5, 2.0)
    ax1.legend(loc="upper left")

    # replicated data (Bayesian model)
    ax2.step(boundaries, step_bayes, where='post', color='#1f77b4', lw=2.5, label="Aggregated SST-GP-GLMM Latent Trajectory Mean")
    for i in range(4):
        ax2.fill_between(
            [boundaries[i], boundaries[i+1]],
            bayes_means[i] - bayes_sds[i],
            bayes_means[i] + bayes_sds[i],
            color='#1f77b4', alpha=0.12
        )
    ax2.set_title("Replication Framework: Aggregated Spatiotemporal Manifold", fontweight='bold', pad=10)
    ax2.set_xlabel("Historical Chronological Horizon (Years CE)", labelpad=10)
    ax2.set_ylabel("Romanticism (Log-Odds)")
    ax2.set_ylim(-1.5, 2.0)
    ax2.legend(loc="upper left")

    # Formatting cleanups
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

if __name__ == "__main__":
    plot_publication_trajectories()
    generate_century_binned_plot()
    plot_paradigm_comparison()
