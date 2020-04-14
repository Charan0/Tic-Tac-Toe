import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]
cx_Freeze.setup(
    name="TicTacToe",
    options={"build_exe": {"packages": ["pygame", "numpy", "tkinter"],
                           "include_files": ["Circle-200.png", "Cross-200.png",
                                             "Heart-AI.png", "Heart-USER.png",
                                             "Poppins.ttf", "Background.mp3"]}},

    description="TicTacToe Game By Charan",
    executables=executables

)
