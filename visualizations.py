"""
Visualizations module for IvyBaseball 

Useful for creating visualizations of college baseball data
# Nathan Blumenfeld
# May 11th 2021
"""
class Figure():
    """
    The main class of the visualizations module. All visualizations are of parent class Figure. 
    
    """
    # ATTRIBUTES (defaults)

    # GETTERS AND SETTERS

    # INITIALIZER
    def __init__(self, style, width=FIGURE_WIDTH, height=FIGURE_HEIGHT):
        """
        Initializes a Figure object with the given style 

        Uses the parent class initializer. By default, x and y are
        GAME_WIDTH/2 and SHIP_BOTTOM, respectively. Also has width,
        height, and source attributes that are SHIP_WIDTH, SHIP_HEIGHT,
        and 'ship_png'.

        Parameter x: The horizontal coordinate of the object center.
        Precondition: x is an int or float.

        Parameter y: The vertical coordinate of the object center.
        Precondition: y is an int or float.
        """
        super().__init__(x=x, y=y, width=SHIP_WIDTH,
                            height=SHIP_HEIGHT, source='ship.png')

    # METHODS
    def _moveShip(self, increment):
        """
        A procedure that modifies the x attribute of a specified Ship object.

        Parameter dx: the desired difference of the x attribute.
        Precondition: dx is an int or float.
        """
        self.x += increment


    def _(self, team_name, start, end):
        """
        generates a cumulative run differential bar chart
        """
        games = sc.get_games(team_name, start=start, end=end)
        games["date"] =  pd.to_datetime(games["date"])
        games = games.sort_values(by="date")
        games = games.reset_index(drop="True")
        games = sc.add_run_difference_column(team_name, games)
        fig = px.bar(games,x=games.index, y="cumulative_rd",
            hover_data=["opponent", "date"], color="cumulative_rd", color_continuous_scale=px.colors.diverging.balance,
            color_continuous_midpoint=0,labels={"cumulative_rd":"Run Differential"})
        fig.update_layout( 
        title = "Cumulative Run Differential<br>"+str(start)+" to "+str(end),
        title_font_size = 20,
        title_xanchor = "center",
        title_yanchor = "top",
        title_x =  0.5,
        yaxis_title="Cumulative Run Differential",
        xaxis_title="Games Played",
        margin=dict(l=40, r=20, t=125, b=20)
        )
        fig.update_yaxes(
        ticklabelposition="inside top",
        )
        fig.update_coloraxes(showscale=False)
        fig.show() 
        

    def generate_ivy_rd_chart(team_name, start, end):
        """
        generates a cumulative run differential bar chart
        """
        games = sc.get_intra_ivy(team_name, start=start, end=end)
        games["date"] = pd.to_datetime(games["date"])
        games = games.sort_values(by="date")
        games = games.reset_index(drop="True")
        games = sc.add_run_difference_column(team_name, games)
        fig = px.bar(games, x=games.index, y="cumulative_rd",
                    hover_data=["opponent", "date"], color="cumulative_rd", color_continuous_scale=px.colors.diverging.balance,
                    color_continuous_midpoint=0, labels={"cumulative_rd": "Run Differential"})
        img = Image.open("resources/logos/"+team_name+".png")
        fig.update_layout(
            title="Cumulative Run Differential<br>"+str(start)+" to "+str(end),
            title_font_size=20,
            title_xanchor="center",
            title_yanchor="top",
            title_x=0.5,
            yaxis_title="Cumulative Run Differential",
            xaxis_title="Games Played",
            margin=dict(l=40, r=20, t=125, b=20)
        )

        fig.update_yaxes(
            ticklabelposition="inside top",
        )
        fig.add_layout_image(
            dict(
                source=img,
                xref="paper", yref="paper",
                xanchor="left", yanchor="top",
                x=-0.02, y=1.325,
                sizex=0.3, sizey=0.3
            )
        )
        fig.update_coloraxes(showscale=False)
        fig.show()
