import pickle
import matplotlib.pyplot as plt
import matplotlib
import itertools
import numpy as np
from builtins import str


class plotter:
    def __init__(self, fontFamily='serif', fontWeight='normal', fontSize=12, lineWidth=1.5, markerSize=7,
                 figsize=(4.5, 3.5), lineStyleData='-', linestyleRef='--', alpha=0.5, markers=None, Grid=True,
                 legend=True, timestep='h'):
        self.fontFamily = fontFamily
        self.fontWeight = fontWeight
        self.fontSize = fontSize
        self.lineWidth = lineWidth
        self.markerSize = markerSize
        self.figSize = figsize
        self.lineStyleData = lineStyleData
        self.lineStyleRef = linestyleRef
        self.alpha = alpha
        if markers != None:
            self.markers = itertools(markers)
        else:
            self.markers = itertools.cycle(('d', 's', '^', 'o', '*'))
        self.grid = Grid
        self.legend = legend
        self.timestep = timestep

        self.font = {}
        self.font['family'] = self.fontFamily
        self.font['weight'] = self.fontWeight
        self.font['size'] = self.fontSize

        matplotlib.rc('text', usetex=True)
        matplotlib.rc('font', **self.font)
        matplotlib.rc('lines', lw=self.lineWidth)

    def __labels(self, string):
        orders = []
        splitted = string.split('_')
        for i in range(len(splitted)):
            if (-1) ** (i + 1) == 1:
                orders.append(splitted[i])
        if len(orders) > 1:
            return r'Stage (I)  ${}$ Stage (II) ${}$'.format(orders[0], orders[1])
        else:
            return r'Stage (I)  ${}$'.format(orders[0])

    def __lineStyles(self,case,differentiate):
        if differentiate:
            caseSplit=case.split('_')
            if len(caseSplit) >2:
                if caseSplit[1]==caseSplit[3] and caseSplit[1]=='p':
                    return '-.'
                else:
                    return self.lineStyleData
            else:
                if caseSplit[1]=='p':
                    return '-.'
                else:
                    return self.lineStyleData
        else:
            return self.lineStyleData

    def __create_key(self, input):
        if len(input) == 2:
            return "s1_{}_s2_{}".format(input[0], input[1])
        if len(input) == 1:
            return "s1_{}".format(input)
        else:
            raise Exception("out of bound !!!")

    def plot(self, path, var, cases=None, refOrder1=False, refOrder2=False, refOrder3=False, textPos=None,
             label_func=None, offset=None, differentiateStyle=False):
        '''
        :param path: path to ups object created after running the script
        :param var: variable name you want to plot ex: x_mom_error
        :param cases: which cases you want to plot ex: [('2','2'),('0','0')] for RK3 or ['2','p'] for RK2
        :param refOrder1: bool show reference for first order
        :param refOrder2: bool show reference for second order
        :param refOrder3: bool show reference for third order
        :param textPos: textPos={'l1':((5e-4, 1.4*1e-3)),
                                 'angle1':80,
                                 'alpha1':0.23e1,
                                 'l2':(5e-4, 2.5*1e-5),
                                 'angle2':8,
                                 'alpha2':0.6e2,
                                 'l3':(5e-4, 2.5*1e-9),
                                 'angle3':1.5e-3,
                                 'alpha3':0.6e2
                                 }
        :param label_func: function, pass a function to change the labeling template
        :param offset: log value to avoid overlaping of cases where we project on all stages and other cases
        :param differentiateStyle: boolian to differentiate the style of  the line where we project on all stages and other lines
        :return:
        '''
        if label_func == None:
            label_func = self.__labels
        objName = path.split('/')[-1]
        title = objName.split('.')[0]
        with open(path, 'rb') as file:
            obj = pickle.load(file)

        fig = plt.figure(figsize=self.figSize)
        ax = fig.add_subplot(1, 1, 1)
        varObj = getattr(obj, var, "{} doesn't exist".format(var))
        if cases == None:
            keys = [*varObj]
        else:
            keys = [self.__create_key(case) for case in cases]

        dts = None
        for num, case in enumerate(keys):
            data = varObj[case]
            if offset == None:
                offval = np.ones_like(data[1])
            else:
                if case == 's1_p' or case == 's1_p_s2_p':
                    offval = np.ones_like(data[1])*offset
                else:
                    offval=np.ones_like(data[1])

            ax.loglog(data[0][:-1], data[1]*offval, marker=next(self.markers), linestyle=self.__lineStyles(case,differentiateStyle),
                      label=label_func(case), markersize=self.markerSize)
            if num == 0:
                dts = np.array(data[0][2:-2])

        # Locations to plot text
        if refOrder1:
            if textPos == None:
                l1 = np.array((5e-4, 1.4 * 1e-3))
                angle1 = 80
                ax.loglog(dts, 0.23e1 * dts, '-k', linestyle='dashed', alpha=0.75)
            else:
                l1 = np.array(textPos['l1'])
                angle1 = textPos['angle1']
                ax.loglog(dts, textPos['alpha1'] * dts, '-k', linestyle='dashed', alpha=0.75)

            trans_angle1 = plt.gca().transData.transform_angles(np.array((angle1,)),
                                                                l1.reshape((1, 2)))[0]
            ax.text(l1[0], l1[1], r'$\mathcal{O}(%s)$' % (self.timestep), fontsize=10,
                    rotation=trans_angle1, rotation_mode='anchor')

        if refOrder2:
            if textPos == None:
                l2 = np.array((5e-4, 2.5 * 1e-5))
                angle2 = 8
                ax.loglog(dts, 0.6e2 * dts ** 2, '-k', linestyle='dashed', alpha=0.75)
            else:
                l2 = np.array(textPos['l2'])
                angle2 = textPos['angle2']
                ax.loglog(dts, textPos['alpha2'] * dts ** 2, '-k', linestyle='dashed', alpha=0.75)

            trans_angle2 = plt.gca().transData.transform_angles(np.array((angle2,)),
                                                                l2.reshape((1, 2)))[0]
            ax.text(l2[0], l2[1], r'$\mathcal{O}(%s^2)$' % (self.timestep), fontsize=10,
                    rotation=trans_angle2, rotation_mode='anchor')

        if refOrder3:
            if textPos == None:
                l3 = np.array((5e-4, 2.8 * 1e-10))
                angle3 = 1e-4
                ax.loglog(dts, 0.2e2 * dts ** 3, '-k', linestyle='dashed', alpha=0.75)
            else:
                l3 = np.array(textPos['l3'])
                angle3 = textPos['angle3']
                ax.loglog(dts, textPos['alpha3'] * dts ** 3, '-k', linestyle='dashed', alpha=0.75)

            trans_angle3 = plt.gca().transData.transform_angles(np.array((angle3,)),
                                                                l3.reshape((1, 2)))[0]
            ax.text(l3[0], l3[1], r'$\mathcal{O}(%s^3)$' % (self.timestep), fontsize=10,
                    rotation=trans_angle3, rotation_mode='anchor')

        ax.set_xlabel(r'$%s$' % (self.timestep))
        ax.set_ylabel(r'$\|L_\infty\|$')

        if self.legend:
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        if self.grid:
            ax.grid(which='both', alpha=self.alpha)
        return ax

# example :
#============
# Initialize the plotter
#------------------------
myp = plotter(timestep='h',legend=False,lineWidth=1.5)

# Plot 1
#--------
cases= ['1','0','p']
separator = '-'
myp.plot('./lid-driven-cavity/RK2SSP.obj','x_mom_error',cases,refOrder1=True,refOrder2=True,offset=np.log(2))
plt.tight_layout()
plt.savefig('./temporal_order_plots/RK2SSP/s1_{}.pdf'.format(separator.join(cases)))
plt.show()

# Plot 2
#--------
cases= [('2','2'),('0','0'),('1','1'),('p','p')]
separator='-'
s1_suffix = [''.join(case[0]) for case in cases]
s2_suffix = [''.join(case[1]) for case in cases]
myp.plot('./lid-driven-cavity/RK3SSP.obj','x_mom_error',cases,refOrder1=True,
refOrder2=True, refOrder3=True,offset=np.log(2))
plt.tight_layout()
plt.savefig('./temporal_order_plots/RK3SSP/s1_{}_s2_{}.pdf'.format(separator.join(s1_suffix),separator.join(s2_suffix)))
plt.show()
