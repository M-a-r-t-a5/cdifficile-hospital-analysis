import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():


    # T# load the dataset and clean the Score column
    def load_and_clean_data(file_name):

        print("\nSTEP 1: Load and clean data\n")
        # read the csv file
        data = pd.read_csv(file_name)

        print(len(data), "rows,", len(data.columns), "columns")

        # Score contains numbers but also text like "Not Available"
        # I turn the text values into NaN so I can use the column for calculations
        data["Score"] = pd.to_numeric(data["Score"],errors="coerce")

        print("Missing Score values:", data["Score"].isnull().sum(), "\n")
        return data

    def explore_data(data):

        print("\nSTEP 2: Dataset overview\n")

        number_hospitals = data["Facility ID"].nunique()
        number_states = data["State"].nunique()
        sir_data = data[data["Measure ID"].str.endswith("_SIR")]

        number_infections = sir_data["Measure Name"].nunique()

        print("Hospitals:", number_hospitals)
        print("States and territories:", number_states)
        print("SIR infection types:", number_infections, "\n")
    


    def compare_cdiff_states(data):

        print("\nSTEP 8: Lowest and highest C. difficile SIR\n")
        if data is None:
            print("ERROR: There is no dataset to analyse.\n")
            return


        sir_data = data[data["Measure ID"].str.endswith("_SIR")]




        # only use C difficile for this part
        cdiff_data = sir_data[sir_data["Measure Name"] == "Clostridium Difficile (C.Diff)"]


        cdiff_data = cdiff_data.dropna(subset=["Score"])


        states = []
        means = []

        uncertainties = []


        state_names = cdiff_data["State"].unique()
        for state in state_names:
            state_data = cdiff_data[cdiff_data["State"] == state]


            scores = np.array(state_data["Score"])
            number_records = len(scores)


            if number_records < 10:
                continue

            mean_sir = np.mean(scores)


            standard_deviation = np.std(scores, ddof=1)
            uncertainty = standard_deviation / np.sqrt(number_records)
            states.append(state)

            means.append(mean_sir)
            uncertainties.append(uncertainty)


        # I need at least two states otherwise there is nothing to compare
        if len(states) < 2:
            print("ERROR: There are not enough states to make a comparison.\n")
            return

        # positions of lowest and highest average
        lowest_position = np.argmin(means)

        highest_position = np.argmax(means)


        lowest_state = states[lowest_position]
        lowest_mean = means[lowest_position]
        lowest_uncertainty = uncertainties[lowest_position]


        highest_state = states[highest_position]

        highest_mean = means[highest_position]
        highest_uncertainty = uncertainties[highest_position]


        # difference between the lowest and highest average
        difference = highest_mean - lowest_mean


        # create the upper and lower uncertainty limits
        lowest_upper = lowest_mean + lowest_uncertainty 
        highest_lower = highest_mean - highest_uncertainty


        print("Lowest:", lowest_state,"=", round(lowest_mean, 3), "+/-", round(lowest_uncertainty, 3))

        print("Highest:", highest_state, "=", round(highest_mean, 3), "+/-", round(highest_uncertainty, 3))

        print("Difference:", round(difference, 3))


        # check if the uncertainty ranges overlap
        if highest_lower > lowest_upper:
            print("Uncertainty ranges do not overlap.\n")

        else:
            print("Uncertainty ranges overlap.\n")




    def analyse_infection_correlations(data):

        print("\nSTEP 10: Infection correlations\n")
        if data is None:
            print("ERROR: There is no dataset to analyse.\n")
            return


        sir_data = data[data["Measure ID"].str.endswith("_SIR")]
        sir_data = sir_data.dropna(subset=["Score"])


        # C difficile is the infection I compare all the others against
        cdiff_data = sir_data[sir_data["Measure Name"] == "Clostridium Difficile (C.Diff)"]
        cdiff_state_average = cdiff_data.groupby("State")["Score"].mean()
        infection_types = sir_data["Measure Name"].unique()


        strongest_correlation = None
        strongest_infection = None

        for infection in infection_types:

            # no reason to compare C difficile with itself
            if infection == "Clostridium Difficile (C.Diff)":
                continue

            infection_data = sir_data[sir_data["Measure Name"] == infection]
            other_state_average = infection_data.groupby("State")["Score"].mean()


            common_states = []
            # only use states where both infections have data
            for state in cdiff_state_average.index:

                if state in other_state_average.index:
                    common_states.append(state)


            if len(common_states) < 2:
                continue

            cdiff_values = []
            other_values = []


            for state in common_states:
                cdiff_values.append(cdiff_state_average[state])

                other_values.append(other_state_average[state])


            correlation = np.corrcoef(cdiff_values,other_values)[0, 1]
            # shorter names again for the output
            if infection == "Central Line Associated Bloodstream Infection (ICU + select Wards)":
                infection_name = "CLABSI"

            elif infection == "Catheter Associated Urinary Tract Infections (ICU + select Wards)":
                infection_name = "CAUTI"

            elif infection == "SSI - Colon Surgery":
                infection_name = "SSI Colon"

            elif infection == "SSI - Abdominal Hysterectomy":
                infection_name = "SSI Hysterectomy"

            elif infection == "MRSA Bacteremia":
                infection_name = "MRSA"
            else:
                infection_name = infection
            print(infection_name,":",round(correlation, 3))

            # save the strongest relationship for the last plot
            if strongest_correlation is None:

                strongest_correlation = correlation
                strongest_infection = infection
            elif abs(correlation) > abs(strongest_correlation):
                strongest_correlation = correlation

                strongest_infection = infection

        if strongest_infection is None:
            print("No valid correlations were found.\n")
            return


        print("\nStrongest correlation:",round(strongest_correlation, 3),"\n")
    def plot_cdiff_distribution(data):

        print("\nSTEP 11: Plot 1: C. difficile distribution\n")

        if data is None:
            print("ERROR: There is no dataset to plot.\n")
            return
        sir_data = data[data["Measure ID"].str.endswith("_SIR")]


        cdiff_data = sir_data[sir_data["Measure Name"] == "Clostridium Difficile (C.Diff)"]


        cdiff_data = cdiff_data.dropna(subset=["Score"])
        scores = np.array(cdiff_data["Score"])
        mean_sir = np.mean(scores)

        median_sir = np.median(scores)
        plt.figure(figsize=(10, 6))


        # histogram shows all hospital values instead of only showing an average
        # I use some transparency so the graph looks less heavy
        plt.hist(scores,bins=30,color="mediumpurple",alpha=0.65,edgecolor="white")

        # Add reference lines so I can compare the distribution
        plt.axvline(x=mean_sir,color="deeppink",linestyle="--",linewidth=2,label="Mean = " + str(round(mean_sir, 3)))

        plt.axvline(x=median_sir,color="purple",linestyle=":",
            linewidth=2,label="Median = " + str(round(median_sir, 3)))

        plt.axvline(x=1,color="red",linestyle="-.",linewidth=2,label="SIR = 1")

        plt.title("Distribution of C. difficile SIR Across US Hospitals",
            fontsize=14,fontweight="bold")
        plt.xlabel("Standardized Infection Ratio",fontsize=11)

        plt.ylabel("Number of Hospitals",fontsize=11)


        plt.legend()
        plt.grid(axis="y",alpha=0.2)


        # this removes the top and right borders and makes it look cleaner
        plt.gca().spines["top"].set_visible(False)

        plt.gca().spines["right"].set_visible(False)


        plt.tight_layout()
        plt.savefig("cdiff_distribution.png", dpi=300, bbox_inches="tight")
        plt.show()

        print("Mean:",round(mean_sir, 3),"| Median:",round(median_sir, 3),"\n")



    def plot_cdiff_state_ranking(data):

        print("\nSTEP 12: Plot 2: Lowest and highest states\n")
        if data is None:
            print("ERROR: There is no dataset to plot.\n")
            return


        sir_data = data[data["Measure ID"].str.endswith("_SIR")]


        cdiff_data = sir_data[sir_data["Measure Name"] == "Clostridium Difficile (C.Diff)"]
        cdiff_data = cdiff_data.dropna(subset=["Score"])


        state_names = []

        state_means = []
        state_uncertainties = []


        states = cdiff_data["State"].unique()


        # get the average and uncertainty for every state
        for state in states:
            state_data = cdiff_data[cdiff_data["State"] == state]


            scores = np.array(state_data["Score"])

            number_records = len(scores)
            if number_records < 10:
                continue


            mean_sir = np.mean(scores)
            standard_deviation = np.std(scores, ddof=1)

            uncertainty = standard_deviation / np.sqrt(number_records)
            state_names.append(state)

            state_means.append(mean_sir)
            state_uncertainties.append(uncertainty)


        # sort everything from lowest SIR to highest
        sort_order = np.argsort(state_means)


        sorted_states = []

        sorted_means = []
        sorted_uncertainties = []


        for position in sort_order:

            sorted_states.append(state_names[position])
            sorted_means.append(state_means[position])

            sorted_uncertainties.append(state_uncertainties[position]) 


        # only show 5 lowest and 5 highest so the graph is not too crowded
        lowest_states = sorted_states[:5]

        lowest_means = sorted_means[:5]
        lowest_uncertainties = sorted_uncertainties[:5]


        highest_states = sorted_states[-5:]

        highest_means = sorted_means[-5:]
        highest_uncertainties = sorted_uncertainties[-5:]


        # I leave a small gap between the lowest and highest groups
        lowest_positions = np.arange(5)
        highest_positions = np.arange(6, 11)


        plt.figure(figsize=(10, 7))

        # lowest states are shown in purple
        plt.errorbar( lowest_means, lowest_positions, xerr=lowest_uncertainties,marker="o", markersize=8,
            color="mediumorchid", ecolor="plum", alpha=0.85, linestyle="none", capsize=4, label="Lowest 5")

        # highest states are shown in red so they stand out
        plt.errorbar( highest_means, highest_positions, xerr=highest_uncertainties, marker="o", markersize=8, color="crimson", ecolor="lightcoral", 
            alpha=0.85, linestyle="none", capsize=4, label="Highest 5" )


        # SIR 1 is still useful as a reference
        plt.axvline(x=1, color="grey", linestyle="--", linewidth=1.5,
            alpha=0.7, label="SIR = 1" )

        all_positions = list(lowest_positions) + list(highest_positions)

        all_states = lowest_states + highest_states


        plt.yticks(all_positions,all_states)


        plt.title("Lowest and Highest C. difficile SIR by State",
            fontsize=14,fontweight="bold")

        plt.xlabel("Average Standardized Infection Ratio",fontsize=11)
        plt.ylabel("State",fontsize=11)


        plt.legend()


        plt.grid(axis="x",alpha=0.2)


        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False)


        plt.tight_layout()
        plt.savefig("state_ranking.png", dpi=300, bbox_inches="tight")        
        plt.show()


    def plot_infection_correlation(data):

        print("\nSTEP 13: Plot 3: Infection correlation\n")

        if data is None:
            print("ERROR: There is no dataset to plot.\n")
            return

        sir_data = data[data["Measure ID"].str.endswith("_SIR")]

        sir_data = sir_data.dropna(subset=["Score"])


        cdiff_data = sir_data[sir_data["Measure Name"] == "Clostridium Difficile (C.Diff)"]


        cdiff_state_average = cdiff_data.groupby("State")["Score"].mean()
        infection_types = sir_data["Measure Name"].unique()


        strongest_correlation = None

        strongest_infection = None

        strongest_cdiff_values = []
        strongest_other_values = []


        for infection in infection_types:

            if infection == "Clostridium Difficile (C.Diff)":
                continue

            infection_data = sir_data[sir_data["Measure Name"] == infection]
            other_state_average = infection_data.groupby("State")["Score"].mean()


            common_states = []


            # find which states have values for both infections
            for state in cdiff_state_average.index:
                if state in other_state_average.index:
                    common_states.append(state)


            if len(common_states) < 2:
                continue


            cdiff_values = []
            other_values = []


            for state in common_states:
                cdiff_values.append(cdiff_state_average[state])

                other_values.append(other_state_average[state])


            correlation = np.corrcoef(cdiff_values,other_values)[0, 1]

            # save whichever infection has the strongest correlation
            if strongest_correlation is None:

                strongest_correlation = correlation
                strongest_infection = infection

                strongest_cdiff_values = cdiff_values

                strongest_other_values = other_values

            elif abs(correlation) > abs(strongest_correlation):

                strongest_correlation = correlation

                strongest_infection = infection
                strongest_cdiff_values = cdiff_values

                strongest_other_values = other_values


        if strongest_infection is None:
            print("ERROR: A valid infection correlation could not be calculated.\n")
            return

        # make the name shorter for the graph
        if strongest_infection == "Central Line Associated Bloodstream Infection (ICU + select Wards)":
            infection_name = "CLABSI"

        elif strongest_infection == "Catheter Associated Urinary Tract Infections (ICU + select Wards)":
            infection_name = "CAUTI"

        elif strongest_infection == "SSI - Colon Surgery":
            infection_name = "SSI Colon"
        elif strongest_infection == "SSI - Abdominal Hysterectomy":
            infection_name = "SSI Hysterectomy"

        elif strongest_infection == "MRSA Bacteremia":
            infection_name = "MRSA"

        else:
            infection_name = strongest_infection


        plt.figure(figsize=(8, 6))


        # Every point is one state
        # transparency helps if some states are close to each other
        plt.scatter(strongest_cdiff_values,strongest_other_values,s=70,
            color="mediumorchid",edgecolor="deeppink",alpha=0.65)


        # calculate a simple straight trend line for the scatter plot
        trend = np.polyfit(strongest_cdiff_values,strongest_other_values,1)

        trend_line = np.poly1d(trend)

        x_values = np.array(strongest_cdiff_values)
        x_sorted = np.sort(x_values)


        plt.plot(x_sorted,trend_line(x_sorted),color="crimson",linewidth=2,alpha=0.8,label="Trend")


        # reference lines for SIR = 1
        plt.axvline(x=1,color="grey",linestyle="--",alpha=0.6)

        plt.axhline(y=1,color="grey",linestyle="--",alpha=0.6)
        plt.title("C. difficile vs " + infection_name+" State Average SIR",fontsize=14,fontweight="bold")

        plt.xlabel("Average C. difficile SIR",fontsize=11)

        plt.ylabel("Average " +infection_name +" SIR",fontsize=11)

        # show the correlation directly on the graph
        plt.text(0.05,0.95,"Correlation = " + str(round(strongest_correlation, 3)),
            transform=plt.gca().transAxes,verticalalignment="top",fontsize=11)


        plt.legend()

        plt.grid(alpha=0.2)
        plt.gca().spines["top"].set_visible(False)

        plt.gca().spines["right"].set_visible(False)


        plt.tight_layout()
        plt.savefig("infection_correlation.png", dpi=300, bbox_inches="tight")
        plt.show()


        print(infection_name,"correlation:",round(strongest_correlation, 3),"\n")
    def print_final_conclusion():

        print("\nFINAL CONCLUSION\n")

        print("Lowest C. difficile SIR = Florida: 0.194 +/- 0.016")
        print("Highest C. difficile SIR = Vermont: 0.840 +/- 0.209")

        print("Difference = 0.646")

        print("Uncertainty ranges do not overlap.\n")

        print("Florida had the lowest average C. difficile SIR")
        print("among the states included in the analysis.\n")



    # this is where the actual program starts after defining all functions
    file_name = "Project/Healthcare_Associated_Infections-Hospital.csv"


    cleaned_data = load_and_clean_data(file_name)
    explore_data(cleaned_data)
    
    
    compare_cdiff_states(cleaned_data)
    analyse_infection_correlations(cleaned_data)

    plot_cdiff_distribution(cleaned_data)
    plot_cdiff_state_ranking(cleaned_data)
    plot_infection_correlation(cleaned_data)

    print_final_conclusion()


main()