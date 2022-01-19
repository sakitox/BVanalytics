# BVanalytics
Data and analytics projects at BuiltVisible

## SEOCausal

### Introduction

Causal Impact is a machine learning model developed by Kay H. Brodersen et al. at Google in 2016. Since then, other leading tech companies have used the open source library to develop their own versions including Uber, Wayfair, and now Builtvisible too!

This algorithm was developed to allow researchers to infer the effect of an intervention applied to a sample or a population.  Causal inference (also known as causal analysis) is tailored to situations in which a controlled randomized experiment (the golden standard in statistical testing),  such as an A/B test, cannot be used. That may be because a classic experiment is either too difficult, too expensive, it is unethical, or simple because it was not done. However, in all such situations we would like to be able to have a quantifiable estimate of the impact our intervention has had, even in the absence of an experiment.

SEO optimization is a domain where causal inference has strong applicability. Once the brilliant team at Builtvisible applies a keyword optimization, a copy-write piece, a link-through implementation, etc. to a single or a group of landing pages (LP) we really lack a control group to compare against. We cannot (easily) split user behavior into control and test groups in most SEO scenarios, once we implement a change, all users will interact with the updated version of the LP. One may argue that if we apply an intervention to a set of LPs then those that did not receive the intervention are, naturally, the control group; however this is bad practice. Each unique LP has an intrinsically unique behavior and any intervention applied will produce a unique impact in terms of all relevant metrics, be it impressions, position, clicks, sessions, or else. By this logic, should we apply the same intervention to a second set of LPs under the same property we would expect different results; invalidating the test/control relationship. The only way we can use traditional statistical experiments in SEO is if we are able to implement changes on a set of LP that only a portion of all users will see, i.e. a classic A/B test.

### Information

- What does the package do?

SEOCausal is an open source library developed at Builtvisible that provides a suite of uplift modeling and causal inference methods using machine learning algorithms based on recent research. 

This library is designed to be quick, flexible, and effective while being tailored for SEO applications.  SEOCausal is designed to handle Google Analytics and Google Search Console data as default inputs but is modular enough to be able to ingest datasets from other sources.

- How does it work?

The workflow to find the estimated impact after an intervention consists of three steps, each defined by its own function, as follows:

  1) Dataset building build():

The first step step takes a global dataset that contains all observations for all markets under study. The global dataset does not need to be sorted or aggregated a priori, it is raw data as obtained from any source. A second dataset is also required as input; it should contain the names of the targeted test markets within the global dataset. 

The output from is a properly formatted and aggregated dataset ready for market matching. All the markets under the test dataset are rolled up into a single group under the name 'TEST'. 

  2) Market matching distance():

This step takes the dataset built during the previous step and finds the distance for every other market in the global dataset against the rolled up 'TEST' market, in a one-to-many fasion. By default only the top 100 best matches are retained in order to speed up the final step of the analysis.

  3) Inference fit():

The final step receives as input a dataset containing the 'TEST' market and a selection of 100 (as default) matched markets. It applies a causal model and returns the estimated impact from the intervention applied. It can display the results in a summary, a plot, or even a full written description depending on the attribute called, see APIs for details.

- What are matching markets?

The function distances() finds the best control markets for the test market by looping through all viable candidates in a parallel fashion and then ranking by their dynamic time warping. Through this process we can find the best control markets and proceed with the selection to the inference step

Dynamic time warping is a technique that finds the distance along the warping curve – instead of the raw data – where the warping curve represents the best alignment between two time series. [1]

- What assumptions does the model make?

As with all non-experimental approaches to causal inference, valid conclusions require strong assumptions. In the case of SEOCausal, we assume that there is a set control time series that were themselves not affected by the intervention. If they were, we might falsely under- or overestimate the true effect. Or we might falsely conclude that there was an effect even though in reality there wasn’t. The model also assumes that the relationship between covariates and the LP that underwent an intervention, as established during the pre-period, remains stable throughout the post-period.
