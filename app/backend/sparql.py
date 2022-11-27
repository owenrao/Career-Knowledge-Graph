########################################
# DSCI 558 Career-SKills Knowledge Graph
# SPRAQL PART
########################################

def get_job_info(position, graph):
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
        res["requiredSkills"] = row.allSkills.split(", ")
        res["relatedTitles"] = row.allTitles.split(", ")
        res["annualSalary"] = row.annual
        res["hourlySalary"] = row.hourly
        
    return res

def get_skill_info(skill, graph):
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
        res["type"] = row.types
        res["category"] = row.categories.split(", ")
        res["isLanguage"] = row.lang
        res["isSoftware"] = row.software
        res["type"] = row.types
        res["source"] = row.source
        res["description"] = row.exp
    
    return res

def filter_skills(category, lang, software, graph):
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