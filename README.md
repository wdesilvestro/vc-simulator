# Venture Capital Simulator

[![VC Simulator Screenshot][screenshot]]([streamlit-link])

## NOTE
This project is no longer maintained. I did not fully implement the [statistical model](https://reactionwheel.net/2017/12/power-laws-in-venture-portfolio-construction.html) suggested by Jerry Neumann, so please review the code in `library.py` to determine if the assumptions made are still of use to you.

## About the project
**Author:** Wes De Silvestro (check out my [blog](https://statespace.blog))

The VC Simulator is a [Streamlit](https://streamlit.io) app that allows users to simulate venture capital funds by tweaking a variety of variables such as the alpha, portfolio size, and fund lifespan.

I built this because I wanted to create a tool to help me build intuition for how VC investing works after reading *The Power Law* by Sebastian Mallaby.


## Getting started
You can play around with the [VC Simulator][streamlit-link] directly in your browser, as it is deployed using Streamlit cloud.

You're also welcome to fork this repository and tweak the underlying model, add graphs/indicators, etc.


## Reporting bugs and making pull requests
You are welcome to report a bug you find in the code by [adding an issue](https://github.com/wdesilvestro/vc-simulator/issues) in GitHub. Or even better: fix it and [make a pull request](https://github.com/wdesilvestro/vc-simulator/pulls) directly.


## Contact
If you have questions about the VC Simulator, please feel free to email me: [wesley.desilvestro@gmail.com](mailto://wesley.desilvestro@gmail.com).


## Acknowledgements and license
This project is distributed under the MIT License. Please see `LICENSE.md` for more details.

Additionally, thank you to the following projects/authors that provided code and write-ups which the VC Simulator is based upon:
- This project would not be possible without the work of Jerry Neumann, a professor at Columbia University, who wrote two blog posts ([here](https://reactionwheel.net/2015/06/power-laws-in-venture.html) and [here](https://reactionwheel.net/2017/12/power-laws-in-venture-portfolio-construction.html)) which were instrumental in constructing this model. Code from the second blog post was also directly utilized in the `library.py` within this project.
- The [Source Sans Pro](https://fonts.google.com/specimen/Source+Sans+Pro) font is included in this repository to help render the graphs. It is provided under the [Open Font License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).
- This project also makes use of the the work of Prakhar Rathi who built a simple library for constructing multi-page Streamlit apps. The `multipage.py` file in this repository is copied directly from [here](https://github.com/prakharrathi25/data-storyteller/) under the MIT License.


<!-- MARKDOWN IMAGES & LINKS -->
[streamlit-link]: https://share.streamlit.io/wdesilvestro/vc-simulator/main/app.py
[screenshot]: images/screenshot.png
