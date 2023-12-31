from IPython import display
from matplotlib import pyplot as plt

plt.ion()

def plot(scores,mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("training")
    plt.xlabel("n_Games")
    plt.ylabel('score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1,scores[-1],str(scores[-1]))
    plt.text(len(mean_scores)-1,mean_scores[-1],str(mean_scores[-1]))