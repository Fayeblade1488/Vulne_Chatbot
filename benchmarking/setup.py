from setuptools import setup, find_packages

setup(
    name='vulne_bench',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'nemoguardrails==0.9.1.1',
        'guardrails-ai',
        'matplotlib==3.8.0',
        'tqdm==4.66.3',
        'reportlab==4.0.4',
        'pytest==7.4.0',
        'bandit==1.7.5',
        'bleach==6.0.0',
        'tenacity==8.2.3',  # For retries
        'psutil==5.9.5',    # For resource monitoring
        'numpy==1.24.3'     # For visualizations
    ],
    entry_points={
        'console_scripts': [
            'run-vulne-bench = vulne_bench.run_all_benchmarks:main',
            'vulne-config = vulne_bench.config_tool:main'
        ]
    }
)
