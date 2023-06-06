import mloop.visualizations as mlv

if __name__ == "__main__":
	mlv.configure_plots()
	mlv.show_all_default_visualizations_from_archive(
		controller_filename=r"C:\Users\YbMinutes\M-LOOP_archives\controller_archive_2022-01-14_10-52.txt",
		learner_filename=r"C:\Users\YbMinutes\M-LOOP_archives\learner_archive_2022-01-14_10-52.txt"
	)