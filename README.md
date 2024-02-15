Quickstart:

1.  Opening the GUI:

    To start the user interface for simulation architecture setup use the command:

         poetry run gui

2.  Performing a simulation:

    To simulate a session save it with the gui and then call:

         poetry run simulate [session_folder_path]"

    To simulate the demo sessions just execute:

         poetry run examples\Demo_01
         poetry run examples\Demo_01

3.  Showing result dashboard on a simulated model run:

    To show the results of a performed simulation execute:

         poetry run dashboard [simulation_object]

    with [simulation_object] being a .sim file within session_folder\simulations
