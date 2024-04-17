import warnings


def suppress_warnings():
    # Suppress the CUDA initialization warning
    warnings.filterwarnings('ignore', message='CUDA initialization.*')

    # Suppress the pretrained parameter deprecated warning
    warnings.filterwarnings('ignore', message="The parameter 'pretrained'.*")

    # Suppress the arguments other than weight enum warning
    warnings.filterwarnings('ignore', message='Arguments other than a weight enum.*')
