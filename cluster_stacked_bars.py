#!/data/apps/enthought_python/2.7.3/bin/python

import pandas as pd
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

def plot_clustered_stacked(dfall, dfup, labels=None, title=" ",  **kwargs):
	"""Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
	labels is a list of the names of the dataframe, used for the legend
	title is a string for the title of the plot
	H is the hatch used for identification of the different dataframe"""
	n_df = len(dfall)
	n_col = len(dfall[0].columns) 
	n_ind = len(dfall[0].index)
	axe = plt.subplot(111)
	ax_inv = axe.twinx()
	hatches = ['\\'*5,' ','-','//','.']
	colors = ['#7d8ca3', '#3e47ab', '#42badb', '#42db78', '#dbdb42', '#e85e27']
	ax_inv = dfup.plot(kind="bar",
					  linewidth=0.8,
					  ax=ax_inv,
					  legend=False,
					  grid=False,
					  color=colors)
	ax_inv.set_ylim(100,0)
	for k,df in enumerate(dfall) : # for each data frame
		axe = df.plot(kind="bar",
					  linewidth=0.8,
					  stacked=True,
					  ax=axe,
					  legend=False,
					  grid=False,
					  color=colors[k],
					  **kwargs)  # make bar plots
	h1,l1 = ax_inv.get_legend_handles_labels()
	for jk, pa1 in enumerate(h1):
		for rect1 in pa1.patches:
			rect1.set_x(rect1.get_x() + 0.45*jk / float(n_df + 1) )
			rect1.set_width(1 / float(n_df + 1))
	h,l = axe.get_legend_handles_labels() # get the handles we want to modify
	for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
		for j, pa in enumerate(h[i:i+n_col]):
			for rect in pa.patches: # for each index
				rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
				rect.set_hatch(hatches[j]) #edited part     
				rect.set_width(1 / float(n_df + 1))
	axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
	axe.set_xticklabels(df.index, rotation = 0)
	axe.set_title(title)
	# Add invisible data to add another legend
	n=[]  
	n1=[]
	for jk in range(n_col):
		n1.append(axe.bar(0,0, color="white", hatch=hatches[jk]))
	for i in range(n_df):
		n.append(axe.bar(0, 0, color=colors[i]))
	l1 = axe.legend(n1[:n_col], l[:n_col], loc=[1.12, 0.5], frameon=False, prop={'size':12})
	if labels is not None:
		l2 = plt.legend(n, labels, loc=[1.12, 0.1], frameon=False, prop={'size':12}) 
	axe.add_artist(l1)
	xlims = list(axe.get_xlim())
	axe.set_xlim(xlims[0], xlims[1]+0.5)
	axe.set_ylim(0,1.5)
	axe.set_xlabel('Date',fontweight='bold')
	axe.set_ylabel('Error Rate',fontweight='bold')
	ax_inv.set_ylabel('# of Effective Snow Sensors',fontweight='bold')
	ax_inv = plt.plot([xlims[0], xlims[1]+0.5],[32,32],'--')
	ax_inv = plt.text(1.3,35,'Total Snow')
	return axe
	
#Real DataFrame

Terra_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Terr_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
Aqua_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Aqua_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
Mitmat_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Mitmat_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
Mitpy_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Mitpy_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
Clearmat_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Clearmat_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
Clearpy_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['Clearpy_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["Omission", "Commision"])
NS_arr67 = pd.DataFrame(scipy.io.loadmat('stat67.mat')['NS_arr67'],
                   index=["24-Mar-2007", "25-Mar-2007", "26-Mar-2007", "27-Mar-2007","28-Mar-2007"],
                   columns=["I", "J","K","L","M","N"])

Terra_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Terr_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
Aqua_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Aqua_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
Mitmat_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Mitmat_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
Mitpy_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Mitpy_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
Clearmat_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Clearmat_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
Clearpy_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['Clearpy_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["Omission", "Commision"])
NS_arr89 = pd.DataFrame(scipy.io.loadmat('stat89.mat')['NS_arr89'],
                   index=["13-Mar-2009", "14-Mar-2009", "15-Mar-2009", "16-Mar-2009","17-Mar-2009"],
                   columns=["I", "J","K","L","M","N"])

plot_clustered_stacked([Terra_arr67, Aqua_arr67, Mitmat_arr67, Mitpy_arr67, Clearmat_arr67, Clearpy_arr67],NS_arr67,["Terra","Aqua","Mitigated by Matlab","Mitigated by Python", "Cleared by Matlab", "Cleared by Python"])

plot_clustered_stacked([Terra_arr89, Aqua_arr89, Mitmat_arr89, Mitpy_arr89, Clearmat_arr89, Clearpy_arr89],NS_arr89,["Terra","Aqua","Mitigated by Matlab","Mitigated by Python", "Cleared by Matlab", "Cleared by Python"])

Mitpy67_time = pd.DataFrame(np.array([[1.645, 0.170, 0.750],[2.032, 2.961, 2.799],[2.411,17.308,4.738], [3.837, 79.262, 5.114]]),
						index=["5 days", "10 days", "20 days", "1 month"],
						columns=["Extracting Constraint Points", "Solving Linear Equation System", "Applying trained weights\n on cloud-hindered images"])

Mitmat67_time = pd.DataFrame(np.array([[1.604, 0.225, 0.974],[2.208, 2.229, 4.844],[2.764, 12.005, 21.598],[3.685, 53.712, 41.057]]),
						index=["5 days", "10 days", "20 days", "1 month"],
						columns=["Extracting Constraint Points", "Solving Linear Equation System", "Applying trained weights\n on cloud-hindered images"])

Mitpy67_point = pd.DataFrame(np.array([[916],[3806],[8146], [13489]]),
							index=["5 days", "10 days", "20 days", "1 month"],
							columns=["Number of Constraint Points"])

Mitmat67_point = pd.DataFrame(np.array([[1254],[4324],[9298], [14945]]),
							index=["5 days", "10 days", "20 days", "1 month"],
							columns=["Number of Constraint Points"])


Mitpy89_time = pd.DataFrame(np.array([[1.545, 1.352, 0.952],[2.015, 12.954, 2.529],[2.467,90.268,4.582], [2.914, 103.137, 5.157]]),
						index=["5 days", "10 days", "20 days", "1 month"],
						columns=["Extracting Constraint Points", "Solving Linear Equation System", "Applying trained weights\n on cloud-hindered images"])

Mitmat89_time = pd.DataFrame(np.array([[2.840, 1.461, 1.477],[3.452, 10.936, 5.126],[3.646, 64.008, 38.765],[5.367, 78.279, 61.286]]),
						index=["5 days", "10 days", "20 days", "1 month"],
						columns=["Extracting Constraint Points", "Solving Linear Equation System", "Applying trained weights\n on cloud-hindered images"])

Mitpy89_point = pd.DataFrame(np.array([[2654],[7566],[15742],[16397]]),
							index=["5 days", "10 days", "20 days", "1 month"],
							columns=["Number of Constraint Points"])

Mitmat89_point = pd.DataFrame(np.array([[3012],[7982],[16112], [16836]]),
							index=["5 days", "10 days", "20 days", "1 month"],
							columns=["Number of Constraint Points"])

CP_points = pd.DataFrame(np.array([916, 1254, 2654, 3012,3806, 4324, 7566, 7982,8146,9298,15742,16112,13489,14945,16397,16836]),
							columns=["Number of Constraint Points"],
							index=["Mitpy67-5days", "Mitmat67-5days", "Mitpy89-5days", "Mitmat89-5days","Mitpy67-10days", "Mitmat67-10days", "Mitpy89-10days", "Mitmat89-10days","Mitpy67-20days", "Mitmat67-20days", "Mitpy89-20days", "Mitmat89-20days","Mitpy67-30days", "Mitmat67-30days", "Mitpy89-30days", "Mitmat89-30days"])
def plot_clustered_stacked2(dfall, dfup, labels=None, title=" ", ylabel=" ", flag=1, **kwargs):
	n_df = len(dfall)
	n_col = len(dfall[0].columns) 
	n_ind = len(dfall[0].index)
	axe = plt.subplot(111)
	ax_inv = axe.twinx()
	hatches = [' ','\\'*5,'/'*5,'-','.']
	colors = ['#4286f4', '#ffb835', '#0d4bad', '#af5700', '#dbdb42', '#e85e27']
	ax_inv.set_ylim(0,20000)
	for k,df in enumerate(dfall) : # for each data frame
		axe = df.plot(kind="bar",
					  linewidth=0.8,
					  stacked=True,
					  ax=axe,
					  legend=False,
					  grid=False,
					  color=colors[k],
					  **kwargs)  # make bar plots
	x_pos = []
	h,l = axe.get_legend_handles_labels() # get the handles we want to modify
	for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
		for j, pa in enumerate(h[i:i+n_col]):
			for rect in pa.patches: # for each index
				x_pos.append(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
				rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
				rect.set_hatch(hatches[j]) #edited part     
				rect.set_width(1 / float(n_df + 1))
	x_pos = sorted(np.unique(x_pos))
	lin = ax_inv.scatter(np.array(x_pos).reshape(-1,1)+0.1, dfup, marker='d', color='red')
	l0=ax_inv.legend(ax_inv.plot(-1,0,color="red",marker='d'),["# of constraint points"],loc=[0.02, 0.73], frameon=False, prop={'size':12})
	ax_inv.add_artist(l0)
	axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
	axe.set_xticklabels(df.index, rotation = 0)
	axe.set_title(title)
	# Add invisible data to add another legend
	n=[]  
	n1=[]
	for jk in range(n_col)[::-1]:
		n1.append(axe.bar(0,0, color="white", hatch=hatches[jk]))
	for i in range(n_df):
		n.append(axe.bar(0, 0, color=colors[i]))
	if flag ==1:
		l1 = axe.legend(n1[:n_col], l[:n_col][::-1], loc=[0.02, 0.8], frameon=False, prop={'size':12})
		axe.add_artist(l1)
	if labels is not None:
		l2 = plt.legend(n, labels, loc=[0.02, 0.6], frameon=False, prop={'size':12}) 
	xlims = list(axe.get_xlim())
	axe.set_xlim(xlims[0], xlims[1]+0.5)
	axe.set_ylim(0, 160)
	axe.set_xlabel('Time Range',fontweight='bold', fontsize=14)
	axe.set_ylabel(ylabel,fontweight='bold', fontsize=14)
	ax_inv.set_ylabel('# of Selected Constraint Points',fontsize=14,fontweight='bold')
	return axe


plot_clustered_stacked2([Mitpy67_time, Mitmat67_time, Mitpy89_time, Mitmat89_time],CP_points,["VI process using Python case # 1","VI process using Matlab case  # 1","VI process using Python case # 2","VI process using Matlab case # 2"]," ","Average time elapsed (seconds)")

plt.show()



