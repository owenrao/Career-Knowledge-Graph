########################################
# DSCI 558 Career-SKills Knowledge Graph
# SPRAQL PART
########################################

def get_job_info(position, graph):
    # Get all info about a job position
    res = {"name": position}
    query = """
        SELECT ?title ?jd ?resp ?annual ?hourly (GROUP_CONCAT(DISTINCT ?skillsName; SEPARATOR = ", ") AS ?allSkills) (GROUP_CONCAT(DISTINCT ?relatedNames; SEPARATOR = ", ") AS ?allTitles)
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name "{}" ;
                   career:relatedSkills ?skills .
            ?skills schema:name ?skillsName .
            ?title career:relatedTitles ?relatedTitles .
            ?relatedTitles schema:name ?relatedNames .
            
            OPTIONAL {{ ?title schema:description ?jd }} .
            OPTIONAL {{ ?title schema:responsibilities ?resp }} .
            OPTIONAL {{ ?title career:annualSalary ?annual }} .
            OPTIONAL {{ ?title career:hourlySalary ?hourly }} .
        }}
        GROUP BY ?title
    """.format(position)
    
    qres = graph.query(query)
    for row in qres:
        res["jobDescription"] = row.jd
        res["responsibility"] = row.resp
        res["requiredSkills"] = sorted(row.allSkills.split(", "))
        res["relatedTitles"] = sorted(row.allTitles.split(", "))
        res["annualSalary"] = row.annual
        res["hourlySalary"] = row.hourly
        
    return res


def get_skill_info(skill, graph):
    # Get all info about a skill
    res = {"name": skill}

    query = """
        SELECT ?skill ?lang ?software (GROUP_CONCAT(DISTINCT ?typeName; SEPARATOR = ", ") AS ?types) (GROUP_CONCAT(DISTINCT ?allCatName; SEPARATOR = ", ") AS ?categories) ?source ?exp
        WHERE {{
            ?skill a career:skill ;
                   schema:name "{}" ;
                   schema:type ?type ;
                   career:isLanguage ?lang ;
                   career:isSoftware ?software .
            ?type schema:name ?typeName .
            OPTIONAL {{ ?skill schema:category ?cat .
                        ?cat schema:object ?allCat .
                        ?allCat schema:name ?allCatName .}} 
            OPTIONAL {{ ?skill schema:description ?dscp .
                        ?dscp career:descriptionSource ?source ;
                              schema:object ?exp .}}
        }}
        GROUP BY ?skill
    """.format(skill)

    qres = graph.query(query)
    for row in qres:
        res["type"] = sorted([i.replace("_", " ") for i in row.types.split(", ")])
        res["category"] = sorted([i.replace("_", " ") for i in row.categories.split(", ")])
        res["isLanguage"] = row.lang
        res["isSoftware"] = row.software
        res["source"] = row.source
        res["description"] = row.exp
    
    return res


def get_related_jobs(position, graph):
    # Get all related jobs for a job position
    res = []

    query = """
        SELECT ?relatedNames ?jd ?resp (GROUP_CONCAT(DISTINCT ?skillsName; SEPARATOR = ", ") AS ?allSkills) ?annual ?hourly
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name "{}" ;
                   career:relatedTitles ?relatedTitles .
            ?relatedTitles schema:name ?relatedNames ;
                           career:relatedSkills ?skills .
            ?skills schema:name ?skillsName .
            OPTIONAL {{ ?relatedTitles schema:description ?jd }} .
            OPTIONAL {{ ?relatedTitles schema:responsibilities ?resp }} .
            OPTIONAL {{ ?relatedTitles career:annualSalary ?annual }} .
            OPTIONAL {{ ?relatedTitles career:hourlySalary ?hourly }} .

        }}
        GROUP BY ?relatedTitles
        ORDER BY ?relatedNames
    """.format(position)

    qres = graph.query(query)
    for row in qres:
        instance = {}
        instance["relatedJob"] = row.relatedNames
        instance["jobDescription"] = row.jd
        instance["responsibility"] = row.resp
        instance["relatedSkills"] = row.allSkills.split(", ")
        instance["annualSalary"] = row.annual
        instance["hourlySalary"] = row.hourly
        res.append(instance)
    
    return res


def get_job_salary(position, graph):
    # Get the average salary for a job position
    res = {"name": position}
    query = """
        SELECT ?title ?annual ?hourly
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name "{}" ;
            
            OPTIONAL {{ ?title career:annualSalary ?annual }} .
            OPTIONAL {{ ?title career:hourlySalary ?hourly }} .

        }}
    """.format(position)
    
    qres = graph.query(query)
    for row in qres:
        res["annualSalary"] = row.annual
        res["hourlySalary"] = row.hourly
        
    return res


def get_job_dscp_resp(position, graph):
    # JD and responsibility for a job position
    res = {"name": position}
    query = """
        SELECT ?title ?jd ?resp
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name "{}" .
            OPTIONAL {{ ?title schema:description ?jd }} .
            OPTIONAL {{ ?title schema:responsibilities ?resp }} .
        }}
    """.format(position)
    
    qres = graph.query(query)
    for row in qres:
        res["jobDescription"] = row.jd
        res["responsibility"] = row.resp

    return res


def get_job_skills(position, graph):
    # Get all related skills for a job position
    res = []
    query = """
        SELECT ?skills ?skillsName ?lang ?software  (GROUP_CONCAT(DISTINCT ?typeName; SEPARATOR = ", ") AS ?types) (GROUP_CONCAT(DISTINCT ?allCatName; SEPARATOR = ", ") AS ?categories) ?source ?exp
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name "{}" ;
                   career:relatedSkills ?skills .
            ?skills schema:name ?skillsName ;
                    schema:type ?type ;
                    career:isLanguage ?lang ;
                    career:isSoftware ?software .
            ?type schema:name ?typeName .
            OPTIONAL {{ ?skills schema:category ?cat .
                        ?cat schema:object ?allCat .
                        ?allCat schema:name ?allCatName . }} 
            OPTIONAL {{ ?skills schema:description ?dscp .
                        ?dscp career:descriptionSource ?source ;
                              schema:object ?exp . }}
        }}
        GROUP BY ?skills
        ORDER BY ?skillsName
    """.format(position)
    
    qres = graph.query(query)
    for row in qres:
        instance = {}
        instance["skill"] = row.skillsName
        instance["type"] = sorted([i.replace("_", " ") for i in row.types.split(", ")])
        instance["category"] = sorted([i.replace("_", " ") for i in row.categories.split(", ")])
        instance["isLanguage"] = row.lang
        instance["isSoftware"] = row.software
        instance["source"] = row.source
        instance["description"] = row.exp
        res.append(instance)
        
    return res


def skill2jobs(skill, graph):
    # Get all jobs that have related skill [SKILL]
    res = []
    query = """
        SELECT ?name ?jd ?resp ?annual ?hourly
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name ?name ;
                   career:relatedSkills ?skills .
            ?skills schema:name "{}" .
            OPTIONAL {{ ?title schema:description ?jd }} .
            OPTIONAL {{ ?title schema:responsibilities ?resp }} .
            OPTIONAL {{ ?title career:annualSalary ?annual }} .
            OPTIONAL {{ ?title career:hourlySalary ?hourly }} .
        }}
        ORDER BY ?name
    """.format(skill)
    
    qres = graph.query(query)
    for row in qres:
        instance = {}
        instance["name"] = row.name
        instance["jobDescription"] = row.jd
        instance["responsibility"] = row.resp
        instance["annualSalary"] = row.annual
        instance["hourlySalary"] = row.hourly
        res.append(instance)
        
    return res


def get_skill_cat(skill, graph):
    # Get all categories and types of a skill
    res = {}

    query = """
        SELECT ?skill (GROUP_CONCAT(DISTINCT ?typeName; SEPARATOR = ", ") AS ?types) (GROUP_CONCAT(DISTINCT ?allCatName; SEPARATOR = ", ") AS ?categories)
        WHERE {{
            ?skill a career:skill ;
                   schema:name "{}" ;
                   schema:type ?type .
            ?type schema:name ?typeName .
            OPTIONAL {{ ?skill schema:category ?cat .
                        ?cat schema:object ?allCat .
                        ?allCat schema:name ?allCatName .}} 
        }}
        GROUP BY ?skill
    """.format(skill)

    qres = graph.query(query)
    for row in qres:
        res["type"] = sorted([i.replace("_", " ") for i in row.types.split(", ")])
        res["category"] = sorted([i.replace("_", " ") for i in row.categories.split(", ")])
        
    return res


def get_job_with_range(keyword, lower, upper, graph):
    # Find jobs which contain keywords and have salary range from min to max
    res = []
    query = """
        SELECT ?title ?name ?jd ?resp ?annual #?hourly (GROUP_CONCAT(DISTINCT ?skillsName; SEPARATOR = ", ") AS ?allSkills)
        WHERE {{
            ?title a schema:Occupation ;
                   schema:name ?name .
            
            OPTIONAL {{ ?title schema:description ?jd }} .
            OPTIONAL {{ ?title schema:responsibilities ?resp }} .
            OPTIONAL {{ ?title career:annualSalary ?annual }} .
            #OPTIONAL {{ ?title career:hourlySalary ?hourly }} .
                        
            FILTER (CONTAINS(LCASE(?name), "{}")) .
            FILTER (?annual >= {} && ?annual <= {}) .
        }}
        ORDER BY ?name
    """.format(keyword.lower(), lower, upper)
    
    qres = graph.query(query)
    for row in qres:
        instance = {}
        instance["name"] = row.name
        instance["jobDescription"] = row.jd
        instance["responsibility"] = row.resp
        instance["annualSalary"] = row.annual
        #instance["Hourly Salary"] = row.hourly
        res.append(instance)
    return res


def get_skills(category, lang, software, graph):
    res = []
    
    if category:
        query = """
            SELECT ?skill ?name ?typeName ?lang ?sw
            WHERE {{
                ?skill a career:skill ;
                       schema:name ?name ;
                       schema:category ?cat ;
                       schema:type ?type ;
                       career:isLanguage ?lang ;
                       career:isSoftware ?sw .
                {}
                {}
                ?type schema:name ?typeName .
                ?cat schema:object ?allCat .
                ?allCat schema:name "%s" .
            }}
            GROUP BY ?skill
            ORDER BY ?name
        """ % category.replace(" ", "_")
    else:
        query = """
            SELECT ?skill ?name ?typeName ?lang ?sw
            WHERE {{
                ?skill a career:skill ;
                       schema:name ?name ;
                       schema:category ?cat ;
                       schema:type ?type ;
                       career:isLanguage ?lang ;
                       career:isSoftware ?sw .
                {}
                {}
                ?type schema:name ?typeName .
            }}
            GROUP BY ?skill
            ORDER BY ?name
        """
    if lang != None and software != None:
        query = query.format("FILTER (?lang = {})".format(lang), "FILTER (?sw = {})".format(software))
    elif lang != None and software == None:
        query = query.format("FILTER (?lang = {})".format(lang), "")
    elif lang == None and software != None:
        query = query.format("FILTER (?sw = {})".format(software), "")
    else:
        query = query.format("", "")

    qres = graph.query(query)
    for row in qres:
        instance = {}
        instance["id"] = row.skill.split("/")[-1]
        instance["name"] = row.name
        instance["tags"] = [row.typeName] if row.typeName != "NULL" else []
        if bool(row.lang):
            instance["tags"].append("Language")
        if bool(row.sw):
            instance["tags"].append("Software")

        res.append(instance)
        
    return res