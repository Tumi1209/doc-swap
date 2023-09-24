from functions import *
from configs import *

st.set_page_config(
    page_title="DocSwap",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🔄",
)


gs_connection = connect_to_gs(st.secrets["gcp_service_account"])
all_swap_data = fetch_swap_data(
    gs_connection, find_swap_table, prod_google_sheet_key, []
)
user_status_data = fetch_status_data(
    gs_connection, status_table, prod_google_sheet_key, []
)
latest_swap_data = get_latest_record_per_email(all_swap_data, user_status_data)
unique_users = count_unique_values(all_swap_data, "email")
unique_swaps = count_unique_values_swapped_yes(user_status_data, "email")


# st.markdown(
#     """
#              #### Welcome to DocSwap! 👋"""
# )

st.markdown(
    """
            #### Welcome to DocSwap! 👋

            ⏳ DocSwap will officially open once the 2024  internship placements are out.

            🗣️ DocSwap works better with more people, share it with other doctors going into their first year of Internship!

            👀 In the meantime, feel free to check out the info tab to see how DocSwap works or reach out [here](https://docs.google.com/forms/d/e/1FAIpQLSfnt0Dq7JBlw-tEUyfVXJueT8aqE3rAcwxoXWWjWi1Jl88gTw/viewform?usp=sf_link) if you have any questions.


            """
)

tab1, tab2 = st.tabs(["Swap", "Info"])

with tab1.expander("🔍 Find a SwapGroup", expanded=False):
    st.markdown(
        """
            🚨 **IMPORTANT:** DocSwap only works for **MBChB** students who are going into their **first** year of internship.

        """
    )

    st.markdown(
        """
            #### Please confirm the following to submit your choices:
        """
    )

    mbchb = st.checkbox("I studied MBChB.")
    intern1 = st.checkbox("I am going into my first year of internship.")
    disclaimer = st.checkbox("I have read the disclaimer.")

    if mbchb and intern1 and disclaimer:
        st.markdown(
            """ Please provide your choices in this [Google form](https://forms.gle/4KQngeC985o782fL6). You will get an email from us if we find a valid swap for you!"""
        )

with tab1.expander("📊 Swap Statistics", expanded=False):
    space1, column, space2 = st.columns([0.1, 0.8, 0.1])
    with column:
        metrics_container = st.container()
        with metrics_container:
            render_svg_banner(
                "diagrams/stats_banner.svg",
                width=100,
                height=100,
                swappers=unique_users,
                emails=unique_swaps,
            )
        st.markdown("""#### """)
        charts_container = st.container()
        with charts_container:
            hist = (
                alt.Chart(latest_swap_data)
                .mark_bar()
                .configure_mark(color="#A398F0")
                .encode(
                    alt.X("count():Q", axis=alt.Axis(title="Number of Posts")),
                    alt.Y(
                        "current_placement:O",
                        axis=alt.Axis(title="Hospital"),
                        sort="-x",
                    ),
                    alt.Order("count():Q", sort="descending"),
                )
            )

            st.subheader(
                "Posts still available for swapping",
                help="The number people at each hospital who are still looking to swap their post. When a swap is found for a given post, it will be removed from this chart, if a person joins DocSwap their post will be added to this chart. If you are not finding any swaps for your choices, check this chart to see if any posts are available at those hospitals.",
            )
            st.altair_chart(
                hist,
                use_container_width=True,
            )


with tab1.expander("🚨 Disclaimer", expanded=False):
    st.markdown(
        """
            1. Swaps are not guaranteed.
            2. Swaps require **everyone** in a SwapGroup to participate, if anyone in a SwapGroup backs out, the group will be invalid and you will need to resubmit your choices so that you can be paired with another SwapGroup.
            3. DocSwap does not manage the logistics of the swap, we simply connect you to a group of valid swappers. You will still need to complete the necessary adminstrative procedures to formalise your swap.
            4. DocSwap takes no responsibility for failed swaps.
    """
    )

with tab1:
    st.markdown(
        """
        ###
                            """
    )

    st.markdown(
        """
                #### Message us on [Telegram!](https://t.me/DocSwapZA)
                                    """
    )

    render_svg(
        "diagrams/telegramqr.svg",
        width=25,
        height=None,
        caption=None,
    )


with tab2.expander("🤔 How does DocSwap work?"):
    st.markdown("### ")
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()

    with row1:
        (
            col1,
            col2,
        ) = st.columns(2)

        with col1:
            image_container = st.container()
            with image_container:
                render_svg(
                    "diagrams/5wayswap.svg",
                    width=90,
                    height=None,
                    caption=None,
                )

        with col2:
            st.markdown(
                """
                        If we think about a swap visually, it's essentially just a closed loop between a group of people. It doesn't matter how many people are in the loop as long as its closed. DocSwap uses your current placement and your three choices to find loops for you. This also allows for much bigger swaps. The biggest swap we've managed to simulate was a 28-way swap, but typically they are around 2-10 people. 
                        """
            )
        st.markdown("### ")
        st.divider()

    with row2:
        (
            col3,
            col4,
        ) = st.columns(2)

        with col3:
            image_container = st.container()
            with image_container:
                render_svg(
                    "diagrams/incomplete.svg",
                    width=90,
                    height=None,
                    caption=None,
                )

        with col4:
            st.markdown(
                """
                As mentioned above, a swap is a **closed** loop of people. If anyone decides not to proceed with the swap, the chain is broken and you will all need to re-apply for a new SwapGroup. To do this you can just repeat the submission process on the Swap page and you will be added back to the selection pool for swapping.

                """
            )

        st.markdown("### ")
        st.divider()

    with row3:
        (
            col5,
            col6,
        ) = st.columns(2)

        with col5:
            image_container = st.container()
            with image_container:
                render_svg(
                    "diagrams/8wayswap.svg",
                    width=90,
                    height=None,
                    caption=None,
                )

        with col6:
            st.markdown(
                """ When we add more people and give each person multiple choices, the number of closed loops we can create becomes exponentially higher. In this image alone we can create 22 closed loops.\nSo how does DocSwap decide on the best loop? Well we give each arrow a weight corresponding to your choice number (eg. choice 1 will get a weight of 1 and choice 2 will get a weight of 2...) and we find the loops with the lowest total weight! Meaning that higher choices are prioritised.
                """
            )

        st.markdown(
            "This also means loops might not contain everyones first choice, since you might need someones third choice to close the loop. So you're probably wondering how you can beat the system? Well we'll tell you, if you are really set on a specific hospital you can choose that hospital for all 3 of your choices... But there's a catch, in doing this you significantly reduce the number of people you can swap with and so your chances of finding a swap group also decrease."
        )

with tab2.expander("💬 Frequently asked questions", expanded=False):
    st.markdown(
        """
                **Q: Someone in my SwapGroup decided they no longer wanted to swap. What should I do now?**\n
                A: Everyone in the SwapGroup will need to re-apply on the Swap page so that we can find alternative SwapGroups for you.
        """
    )

    st.divider()

    st.markdown(
        """
                **Q: I have already swapped but feel I can still do better, can I swap again?**\n
                A: Yes, you can swap as many times as you want, just make sure you re-apply with your latest placement.
        """
    )

    st.divider()

    st.markdown(
        """
                **Q: Does DocSwap work for other degrees or comm serve?**\n
                A: At the moment no. However, we can set up a custom version to work for a different degree if there is enough demand. Message us on [Telegram](https://t.me/DocSwapZA) if you want to chat more on this.
        """
    )

    st.divider()

    st.markdown(
        """
                **Q: How does DocSwap make money?**\n
                A: It doesn't.
        """
    )

    st.divider()

    st.markdown(
        """
                **Q: Do you sell our email addresses or other data?**\n
                A: No, all information is confidential.
        """
    )

    st.divider()

    st.markdown(
        """
                **Q: Will submitting mutliple times give me more choices or better odds at finding a SwapGroup**\n
                A: No, I only take the latest submission per user.
        """
    )


with tab2.expander("📞 Contact us?", expanded=False):
    st.markdown(
        """
                Reach out using this [FORM](https://docs.google.com/forms/d/e/1FAIpQLSfnt0Dq7JBlw-tEUyfVXJueT8aqE3rAcwxoXWWjWi1Jl88gTw/viewform?usp=sf_link) and we'll get back to you.

        """
    )
