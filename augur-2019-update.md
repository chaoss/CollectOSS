# Augur Update, 2019
Augur is an increasingly robust, systematically designed data collection, analytical and notification system for making sense of the health and sustainability of open source software project health and sustainability. We maintain our identity as a prototyping system, and expect the innovations we have developed in the past year will inspire other projects, and are proud of the organizations, open source program offices, and open source community managers we have helped through our work. Remy DeCausemaker from Twitter is a tireless, friendly source of inspiration and constructive critique that influenced our choice to evaluate and reconstruct the hear of Augur this year. Our Google summer of code students Parth and Bingwen worked hard with our core Augur team of Gabe Heim, Carter Landis, Derek Howard, and Jonah Zukowsky through the summer to make our new vision for Augur real. New team members, Elita Nelson, Carolyn Periciniaro, Paul Orton and Sean's computer science undergraduate students are a part of Augur's growing core contributors. Proof, in a sense, that we are learning how to onboard new contributors more effectively. 

# Augur's 2018-2019 design and implementation evolution points include: 
1. Working with CHAOSS's stakeholder community we designed and implemented a comprehensive, unified data model that brings together insights from Brian Warner's Facade Project, Libraries.io, GHTorrent, DOSoCs (now "chaoss/augur-sbom"), Brian Proffit's, Dawn Foster's and GrimoireLab's insights about individual identity and organizational affiliation complexity. A single data model that stores system-specific software engineering synonyms for "commit", "issue", "pull request", and other constructs. 
2. The unified data model accelerates analysis of open source ecosystems, and projects that are managed in heterogeneous .git infrastructure. 
3. To collect data, Augur now relies on a federated broker-worker system. Six workers are presently deployed and operating against over 15,000 repositories for a diverse group of open source stakeholders. Each worker continuously collects data, and sends it to the broker, who stores the data. A Housekeeper makes sure every worker keeps doing their job. 
4. A new design of our API endpoints follows a common :repo_id/name and :repo_group(project)_id/name standard that eases the implementation of customized, organization specific distribution of Augur data. 
5. Augur's front end is completely redesigned and rewritten using Typescript instead of Javascript, which is lowering our change and maintenance costs. 
6. The number of Augur deployments continues to grow, and our newcomer experience is significantly improved since March, 2019. 
7. Our collaborations with the Grace Hopper Conference, including an Augur workshop, is helping to push these advances forward.
8. We now use machine learning and statistical algorithms to identify events buried in the 60+ metrics endpoints our restful API now supports. 
9. The resulting insights are provided via push notifications in Slack, email and other messenger clients.  
10. Augur's front end and back end are now independently deployable, meaning that new users can use Augur only for API's it uses to feed their own systems, or begin to work with our front end. 

# Augur's 2019-2020 Goals include: 
1. Integration of HyperLedger/Indy for federated, secure single sign on. 
2. Continued advances in deployment of our machine learning anomaly detection, and push notification system. 
3. Creating CHAOSS metrics from the 24 Augur endpoints that are not currently defined as CHAOSS metrics. 
4. Implementation of our value workers based on the COCOMO model of software engineering labor and cost estimation
5. Implementation of test coverage metrics from the Risk working group. 
6. Providing technical infrastructure to enable diversity and inclusion working group process aims to be supported in context with Augur's whole system. 
7. Incorporating important content directing Augur users to resources for risk management, value assessment, diversity and inclusion awareness and organizational and individual developer information. 
8. A user configurable mechanism for deriving user directed "dashboard indicators" of comparative health within their ecosystem. 
