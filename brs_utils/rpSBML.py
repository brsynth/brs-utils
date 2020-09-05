import libsbml
import logging
import numpy as np
from hashlib import sha256
from os      import makedirs  as os_mkdirs
from os      import path      as os_path
from copy    import deepcopy
from pandas  import DataFrame as pd_DataFrame

## @package RetroPath SBML writer
# Documentation for SBML representation of the different model
#
# To exchange between the different workflow nodes, the SBML (XML) format is used. This
# implies using the libSBML library to create the standard definitions of species, reactions, etc...
# Here we also define our own annotations that are used internally in that we call BRSYNTH nodes.
# The object holds an SBML object and a series of methods to write and access BRSYNTH related annotations


# logging = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)


##################################################################
############################### rpSBML ###########################
##################################################################


## libSBML reader for RetroPath
# Converts an SBML object (or file) into the internal format
#
class rpSBML:
    ## Constructor
    #
    # @param model libSBML model object
    # @param docModel libSBML Document object
    # @param nameSpaceModel libSBML name space (not required)
    def __init__(self, modelName, document=None, path=None):
        #WARNING: change this to reflect the different debugging levels
#        logging.info('Started instance of rpSBML')
        #logging.setLevel(logging.INFO)
        self.modelName = modelName
        self.document = document
        if self.document==None:
            self.model = None
        else:
            self.model = self.document.getModel()
        #@Joan I keep this commented since I use the rpSBML(path='') and not sure if you made changes
        '''
        self.path = path
        #More complete with
        #self.miriam_header = {'compartment': {'go': 'go/GO:', 'mnx': 'metanetx.compartment/', 'bigg': 'bigg.compartment/', 'seed': 'seed/', 'name': 'name/'}, 'reaction': {'mnx': 'metanetx.reaction/', 'rhea': 'rhea/', 'reactome': 'reactome/', 'bigg': 'bigg.reaction/', 'sabiork': 'sabiork.reaction/', 'ec': 'ec-code/', 'biocyc': 'biocyc/', 'lipidmaps': 'lipidmaps/', 'uniprot': 'uniprot/'}, 'species': {'mnx': 'metanetx.chemical/', 'chebi': 'chebi/CHEBI:', 'bigg': 'bigg.metabolite/', 'hmdb': 'hmdb/', 'kegg_c': 'kegg.compound/', 'kegg_d': 'kegg.drug/', 'biocyc': 'biocyc/META:', 'seed': 'seed.compound/', 'metacyc': 'metacyc.compound/', 'sabiork': 'sabiork.compound/', 'reactome': 'reactome/R-ALL-'}}
        #self.header_miriam = {'compartment': {'go': 'go', 'metanetx.compartment': 'mnx', 'bigg.compartment': 'bigg', 'seed': 'seed', 'name': 'name'}, 'reaction': {'metanetx.reaction': 'mnx', 'rhea': 'rhea', 'reactome': 'reactome', 'bigg.reaction': 'bigg', 'sabiork.reaction': 'sabiork', 'ec-code': 'ec', 'biocyc': 'biocyc', 'lipidmaps': 'lipidmaps', 'uniprot': 'uniprot'}, 'species': {'metanetx.chemical': 'mnx', 'chebi': 'chebi', 'bigg.metabolite': 'bigg', 'hmdb': 'hmdb', 'kegg.compound': 'kegg_c', 'kegg.drug': 'kegg_d', 'biocyc': 'biocyc', 'seed.compound': 'seed', 'metacyc.compound': 'metacyc', 'sabiork.compound': 'sabiork', 'reactome': 'reactome'}}
        #removed GO
        self.miriam_header = {'compartment': {'mnx': 'metanetx.compartment/', 'bigg': 'bigg.compartment/', 'seed': 'seed/', 'name': 'name/'}, 'reaction': {'mnx': 'metanetx.reaction/', 'rhea': 'rhea/', 'reactome': 'reactome/', 'bigg': 'bigg.reaction/', 'sabiork': 'sabiork.reaction/', 'ec': 'ec-code/', 'biocyc': 'biocyc/', 'lipidmaps': 'lipidmaps/', 'uniprot': 'uniprot/'}, 'species': {'pubchem': 'pubchem.compound/','mnx': 'metanetx.chemical/', 'chebi': 'chebi/CHEBI:', 'bigg': 'bigg.metabolite/', 'hmdb': 'hmdb/', 'kegg_c': 'kegg.compound/', 'kegg_d': 'kegg.drug/', 'biocyc': 'biocyc/META:', 'seed': 'seed.compound/', 'metacyc': 'metacyc.compound/', 'sabiork': 'sabiork.compound/', 'reactome': 'reactome/R-ALL-'}}
        self.header_miriam = {'compartment': {'metanetx.compartment': 'mnx', 'bigg.compartment': 'bigg', 'seed': 'seed', 'name': 'name'}, 'reaction': {'metanetx.reaction': 'mnx', 'rhea': 'rhea', 'reactome': 'reactome', 'bigg.reaction': 'bigg', 'sabiork.reaction': 'sabiork', 'ec-code': 'ec', 'biocyc': 'biocyc', 'lipidmaps': 'lipidmaps', 'uniprot': 'uniprot'}, 'species': {'pubchem.compound': 'pubchem', 'metanetx.chemical': 'mnx', 'chebi': 'chebi', 'bigg.metabolite': 'bigg', 'hmdb': 'hmdb', 'kegg.compound': 'kegg_c', 'kegg.drug': 'kegg_d', 'biocyc': 'biocyc', 'seed.compound': 'seed', 'metacyc.compound': 'metacyc', 'sabiork.compound': 'sabiork', 'reactome': 'reactome'}}
        '''
        if not path==None:
            self.path = path
            self.readSBML(path)
        else:
            self.path = None
        self.rules_scores = (-1, 0)
        self.miriam_header = {'compartment': {'mnx': 'metanetx.compartment/', 'bigg': 'bigg.compartment/', 'seed': 'seed/', 'name': 'name/'}, 'reaction': {'mnx': 'metanetx.reaction/', 'rhea': 'rhea/', 'reactome': 'reactome/', 'bigg': 'bigg.reaction/', 'sabiork': 'sabiork.reaction/', 'ec': 'ec-code/', 'biocyc': 'biocyc/', 'lipidmaps': 'lipidmaps/', 'uniprot': 'uniprot/'}, 'species': {'inchikey': 'inchikey/', 'pubchem': 'pubchem.compound/','mnx': 'metanetx.chemical/', 'chebi': 'chebi/CHEBI:', 'bigg': 'bigg.metabolite/', 'hmdb': 'hmdb/', 'kegg_c': 'kegg.compound/', 'kegg_d': 'kegg.drug/', 'biocyc': 'biocyc/META:', 'seed': 'seed.compound/', 'metacyc': 'metacyc.compound/', 'sabiork': 'sabiork.compound/', 'reactome': 'reactome/R-ALL-'}}
        self.header_miriam = {'compartment': {'metanetx.compartment': 'mnx', 'bigg.compartment': 'bigg', 'seed': 'seed', 'name': 'name'}, 'reaction': {'metanetx.reaction': 'mnx', 'rhea': 'rhea', 'reactome': 'reactome', 'bigg.reaction': 'bigg', 'sabiork.reaction': 'sabiork', 'ec-code': 'ec', 'biocyc': 'biocyc', 'lipidmaps': 'lipidmaps', 'uniprot': 'uniprot'}, 'species': {'inchikey': 'inchikey', 'pubchem.compound': 'pubchem', 'metanetx.chemical': 'mnx', 'chebi': 'chebi', 'bigg.metabolite': 'bigg', 'hmdb': 'hmdb', 'kegg.compound': 'kegg_c', 'kegg.drug': 'kegg_d', 'biocyc': 'biocyc', 'seed.compound': 'seed', 'metacyc.compound': 'metacyc', 'sabiork.compound': 'sabiork', 'reactome': 'reactome'}}

    #############################################################################################################
    ############################################ MERGE ##########################################################
    #############################################################################################################

    @staticmethod
    def mergeSBMLFiles(path_source,
                       path_target,
                       path_merge,
                       species_group_id='central_species',
                       sink_species_group_id='rp_sink_species',
                       pathway_id='rp_pathway'):
        if not os_path.exists(path_source):
            logging.error('Source SBML file is invalid: '+str(path_source))
            return False
        if not os_path.exists(path_target):
            logging.error('Target SBML file is invalid: '+str(path_target))
            return False
        source_rpsbml = rpSBML.rpSBML('source', path=path_source)
        target_rpsbml = rpSBML.rpSBML('target', path=path_target)
        rpSBML.mergeModels(source_rpsbml,
                           target_rpsbml,
                           species_group_id,
                           sink_species_group_id,
                           pathway_id)
        target_rpsbml.writeSBML(path_merge)
        return True

    @staticmethod
    ## Merge two models species and reactions using the annotations to recognise the same species and reactions
    #
    # The source model has to have both the GROUPS and FBC packages enabled in its SBML. The course must have a groups
    #called rp_pathway. If not use the readSBML() function to create a model
    # We add the reactions and species from the rpsbml to the target_model
    #
    # @param target_model input libsbml model object where we will add the reactions and species from self.model
    # @param pathway_id String default is rp_pathway, name of the pathway id of the groups object
    # @param addOrphanSpecies Boolean Default False
    # @param bilevel_obj Tuple of size 2 with the weights associated with the targetSink and GEM objective function
    #
    #TODO: add a confidence in the merge using the score in
    #TODO: seperate the different parts so that others may use it
    def mergeModels(source_rpsbml,
                    target_rpsbml,
                    species_group_id='central_species',
                    sink_species_group_id='rp_sink_species',
                    pathway_id='rp_pathway'):
        #target_rpsbml.model = target_document.getModel()
        #Find the ID's of the similar target_rpsbml.model species
        ################ MODEL FBC ########################
        if not target_rpsbml.model.isPackageEnabled('fbc'):
            rpSBML._checklibSBML(target_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/fbc/version2',
                'fbc',
                True),
                    'Enabling the FBC package')
        if not source_rpsbml.model.isPackageEnabled('fbc'):
            rpSBML._checklibSBML(source_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/fbc/version2',
                'fbc',
                True),
                    'Enabling the FBC package')
        target_fbc = target_rpsbml.model.getPlugin('fbc')
        source_fbc = source_rpsbml.model.getPlugin('fbc')
        #note sure why one needs to set this as False
        rpSBML._checklibSBML(source_rpsbml.document.setPackageRequired('fbc', False), 'enabling FBC package')
        ################ UNITDEFINITIONS ######
        #return the list of unit definitions id's for the target to avoid overwritting
        #WARNING: this means that the original unit definitions will be prefered over the new one
        target_unitDefID = [i.getId() for i in target_rpsbml.model.getListOfUnitDefinitions()]
        for source_unitDef in source_rpsbml.model.getListOfUnitDefinitions():
            if not source_unitDef.getId() in target_unitDefID: #have to compare by ID since no annotation
                #create a new unitDef in the target
                target_unitDef = target_rpsbml.model.createUnitDefinition()
                rpSBML._checklibSBML(target_unitDef, 'fetching target unit definition')
                #copy unitDef info to the target
                rpSBML._checklibSBML(target_unitDef.setId(source_unitDef.getId()),
                    'setting target unit definition ID')
                rpSBML._checklibSBML(target_unitDef.setAnnotation(source_unitDef.getAnnotation()),
                    'setting target unit definition Annotation')
                for source_unit in source_unitDef.getListOfUnits():
                    #copy unit info to the target unitDef
                    target_unit = target_unitDef.createUnit()
                    rpSBML._checklibSBML(target_unit, 'creating target unit')
                    rpSBML._checklibSBML(target_unit.setKind(source_unit.getKind()),
                        'setting target unit kind')
                    rpSBML._checklibSBML(target_unit.setExponent(source_unit.getExponent()),
                        'setting target unit exponent')
                    rpSBML._checklibSBML(target_unit.setScale(source_unit.getScale()),
                        'setting target unit scale')
                    rpSBML._checklibSBML(target_unit.setMultiplier(source_unit.getMultiplier()),
                        'setting target unit multiplier')
                target_unitDefID.append(source_unitDef.getId()) #add to the list to make sure its not added twice
        ################ COMPARTMENTS ###############
        # Compare by MIRIAM annotations
        #Note that key is source and value is target conversion
        comp_source_target = {}
        for source_compartment in source_rpsbml.model.getListOfCompartments():
            found = False
            target_ids = [i.getId() for i in target_rpsbml.model.getListOfCompartments()]
            source_annotation = source_compartment.getAnnotation()
            if not source_annotation:
                logging.warning('No annotation for the source of compartment '+str(source_compartment.getId()))
                continue
            #compare by MIRIAM first
            for target_compartment in target_rpsbml.model.getListOfCompartments():
                target_annotation = target_compartment.getAnnotation()
                if not target_annotation:
                    logging.warning('No annotation for the target of compartment: '+str(target_compartment.getId()))
                    continue
                if source_rpsbml.compareMIRIAMAnnotations(source_annotation, target_annotation):
                    found = True
                    comp_source_target[source_compartment.getId()] = target_compartment.getId()
                    break
            if not found:
                #if the id is not found, see if the ids already exists
                if source_compartment.getId() in target_ids:
                    comp_source_target[source_compartment.getId()] = source_compartment.getId()
                    found = True
                #if there is not MIRIAM match and the id's differ then add it
                else:
                    target_compartment = target_rpsbml.model.createCompartment()
                    rpSBML._checklibSBML(target_compartment, 'Creating target compartment')
                    rpSBML._checklibSBML(target_compartment.setMetaId(source_compartment.getMetaId()),
                            'setting target metaId')
                    #make sure that the ID is different
                    if source_compartment.getId()==target_compartment.getId():
                        rpSBML._checklibSBML(target_compartment.setId(source_compartment.getId()+'_sourceModel'),
                                'setting target id')
                    else:
                        rpSBML._checklibSBML(target_compartment.setId(source_compartment.getId()),
                                'setting target id')
                    rpSBML._checklibSBML(target_compartment.setName(source_compartment.getName()),
                            'setting target name')
                    rpSBML._checklibSBML(target_compartment.setConstant(source_compartment.getConstant()),
                            'setting target constant')
                    rpSBML._checklibSBML(target_compartment.setAnnotation(source_compartment.getAnnotation()),
                            'setting target annotation')
                    rpSBML._checklibSBML(target_compartment.setSBOTerm(source_compartment.getSBOTerm()),
                            'setting target annotation')
                    comp_source_target[target_compartment.getId()] = target_compartment.getId()
        logging.debug('comp_source_target: '+str(comp_source_target))
        ################ PARAMETERS ###########
        #WARNING: here we compare by ID
        targetParametersID = [i.getId() for i in target_rpsbml.model.getListOfParameters()]
        for source_parameter in source_rpsbml.model.getListOfParameters():
            if not source_parameter.getId() in targetParametersID:
                target_parameter = target_rpsbml.model.createParameter()
                rpSBML._checklibSBML(target_parameter, 'creating target parameter')
                rpSBML._checklibSBML(target_parameter.setId(source_parameter.getId()), 'setting target parameter ID')
                rpSBML._checklibSBML(target_parameter.setSBOTerm(source_parameter.getSBOTerm()),
                    'setting target parameter SBO')
                rpSBML._checklibSBML(target_parameter.setUnits(source_parameter.getUnits()),
                    'setting target parameter Units')
                rpSBML._checklibSBML(target_parameter.setValue(source_parameter.getValue()),
                    'setting target parameter Value')
                rpSBML._checklibSBML(target_parameter.setConstant(source_parameter.getConstant()),
                    'setting target parameter ID')
        ################ FBC GENE PRODUCTS ########################
        #WARNING: here we compare by ID
        targetGenProductID = [i.getId() for i in target_fbc.getListOfGeneProducts()]
        for source_geneProduct in source_fbc.getListOfGeneProducts():
            if not source_geneProduct.getId() in targetGenProductID:
                target_geneProduct = target_fbc.createGeneProduct()
                rpSBML._checklibSBML(target_geneProduct, 'creating target gene product')
                rpSBML._checklibSBML(target_geneProduct.setId(source_geneProduct.getId()),
                    'setting target gene product id')
                rpSBML._checklibSBML(target_geneProduct.setLabel(source_geneProduct.getLabel()),
                    'setting target gene product label')
                rpSBML._checklibSBML(target_geneProduct.setName(source_geneProduct.getName()),
                    'setting target gene product name')
                rpSBML._checklibSBML(target_geneProduct.setMetaId(source_geneProduct.getMetaId()),
                    'setting target gene product meta_id')
        ############### FBC OBJECTIVES ############
        #WARNING: here we compare by ID
        targetObjectiveID = [i.getId() for i in target_fbc.getListOfObjectives()]
        sourceObjectiveID = [i.getId() for i in source_fbc.getListOfObjectives()]
        for source_objective in source_fbc.getListOfObjectives():
            if not source_objective.getId() in targetObjectiveID:
                target_objective = target_fbc.createObjective()
                rpSBML._checklibSBML(target_objective, 'creating target objective')
                rpSBML._checklibSBML(target_objective.setId(source_objective.getId()), 'setting target objective')
                rpSBML._checklibSBML(target_objective.setName(source_objective.getName()), 'setting target objective')
                rpSBML._checklibSBML(target_objective.setType(source_objective.getType()),
                        'setting target objective type')
                for source_fluxObjective in source_objective.getListOfFluxObjectives():
                    target_fluxObjective = target_objective.createFluxObjective()
                    rpSBML._checklibSBML(target_fluxObjective, 'creating target flux objective')
                    rpSBML._checklibSBML(target_fluxObjective.setName(source_fluxObjective.getName()),
                        'setting target flux objective name')
                    rpSBML._checklibSBML(target_fluxObjective.setCoefficient(source_fluxObjective.getCoefficient()),
                        'setting target flux objective coefficient')
                    rpSBML._checklibSBML(target_fluxObjective.setReaction(source_fluxObjective.getReaction()),
                        'setting target flux objective reaction')
                    rpSBML._checklibSBML(target_fluxObjective.setAnnotation(source_fluxObjective.getAnnotation()),
                        'setting target flux obj annotation from source flux obj')
                rpSBML._checklibSBML(target_objective.setAnnotation(source_objective.getAnnotation()),
                        'setting target obj annotation from source obj')
        logging.debug('targetObjectiveID: '+str(targetObjectiveID))
        logging.debug('sourceObjectiveID: '+str(sourceObjectiveID))
        ################ SPECIES ####################
        species_source_target = rpSBML.compareSpecies(comp_source_target, source_rpsbml, target_rpsbml)
        logging.debug('species_source_target: '+str(species_source_target))
        for source_species in species_source_target:
            list_target = [i for i in species_source_target[source_species]]
            if source_species in list_target:
                logging.warning('The source ('+str(source_species)+') and target species ids ('+str(list_target)+') are the same')
            #if no match then add it to the target model
            if species_source_target[source_species]=={}:
                logging.debug('Creating source species '+str(source_species)+' in target rpsbml')
                source_species = source_rpsbml.model.getSpecies(source_species)
                if not source_species:
                    logging.error('Cannot retreive model species: '+str(source_species))
                else:
                    rpSBML._checklibSBML(source_species, 'fetching source species')
                    targetModel_species = target_rpsbml.model.createSpecies()
                    rpSBML._checklibSBML(targetModel_species, 'creating species')
                    rpSBML._checklibSBML(targetModel_species.setMetaId(source_species.getMetaId()),
                            'setting target metaId')
                    rpSBML._checklibSBML(targetModel_species.setId(source_species.getId()),
                            'setting target id')
                    rpSBML._checklibSBML(targetModel_species.setCompartment(comp_source_target[source_species.getCompartment()]),
                            'setting target compartment')
                    rpSBML._checklibSBML(targetModel_species.setInitialConcentration(
                        source_species.getInitialConcentration()),
                            'setting target initial concentration')
                    rpSBML._checklibSBML(targetModel_species.setBoundaryCondition(
                        source_species.getBoundaryCondition()),
                            'setting target boundary concentration')
                    rpSBML._checklibSBML(targetModel_species.setHasOnlySubstanceUnits(
                        source_species.getHasOnlySubstanceUnits()),
                            'setting target has only substance units')
                    rpSBML._checklibSBML(targetModel_species.setBoundaryCondition(
                        source_species.getBoundaryCondition()),
                            'setting target boundary condition')
                    rpSBML._checklibSBML(targetModel_species.setConstant(source_species.getConstant()),
                        'setting target constant')
                    rpSBML._checklibSBML(targetModel_species.setAnnotation(source_species.getAnnotation()),
                        'setting target annotation')
        ################ REACTIONS ###################
        #TODO; consider the case where two reactions have the same ID's but are not the same reactions
        reac_replace = {}
        for source_reaction in source_rpsbml.model.getListOfReactions():
            is_found = False
            for target_reaction in target_rpsbml.model.getListOfReactions():
                score, match = rpSBML.compareReaction(species_source_target, source_reaction, target_reaction)
                if match:
                    logging.debug('Source reaction '+str(source_reaction)+' matches with target reaction '+str(target_reaction))
                    #source_reaction[source_reaction.getId()] = target_reaction.getId()
                    reac_replace[source_reaction.getId()] = target_reaction.getId()
                    is_found = True
                    break
            if not is_found:
                logging.debug('Cannot find source reaction: '+str(source_reaction.getId()))
                rpSBML._checklibSBML(source_reaction, 'fetching source reaction')
                target_reaction = target_rpsbml.model.createReaction()
                rpSBML._checklibSBML(target_reaction, 'create reaction')
                target_fbc = target_reaction.getPlugin('fbc')
                rpSBML._checklibSBML(target_fbc, 'fetching target FBC package')
                source_fbc = source_reaction.getPlugin('fbc')
                rpSBML._checklibSBML(source_fbc, 'fetching source FBC package')
                source_upperFluxBound = source_fbc.getUpperFluxBound()
                rpSBML._checklibSBML(source_upperFluxBound, 'fetching upper flux bound')
                rpSBML._checklibSBML(target_fbc.setUpperFluxBound(source_upperFluxBound),
                        'setting upper flux bound')
                source_lowerFluxBound = source_fbc.getLowerFluxBound()
                rpSBML._checklibSBML(source_lowerFluxBound, 'fetching lower flux bound')
                rpSBML._checklibSBML(target_fbc.setLowerFluxBound(source_lowerFluxBound),
                        'setting lower flux bound')
                rpSBML._checklibSBML(target_reaction.setId(source_reaction.getId()), 'set reaction id')
                rpSBML._checklibSBML(target_reaction.setName(source_reaction.getName()), 'set name')
                rpSBML._checklibSBML(target_reaction.setSBOTerm(source_reaction.getSBOTerm()),
                        'setting the reaction system biology ontology (SBO)') #set as process
                #TODO: consider having the two parameters as input to the function
                rpSBML._checklibSBML(target_reaction.setReversible(source_reaction.getReversible()),
                        'set reaction reversibility flag')
                rpSBML._checklibSBML(target_reaction.setFast(source_reaction.getFast()),
                        'set reaction "fast" attribute')
                rpSBML._checklibSBML(target_reaction.setMetaId(source_reaction.getMetaId()), 'setting species meta_id')
                rpSBML._checklibSBML(target_reaction.setAnnotation(source_reaction.getAnnotation()),
                        'setting annotation for source reaction')
                #Reactants
                logging.debug('Setting reactants')
                for source_reaction_reactantID in [i.species for i in source_reaction.getListOfReactants()]:
                    logging.debug('\tAdding '+str(source_reaction_reactantID))
                    target_reactant = target_reaction.createReactant()
                    rpSBML._checklibSBML(target_reactant, 'create target reactant')
                    if source_reaction_reactantID in species_source_target:
                        if not species_source_target[source_reaction_reactantID]=={}:
                            if len(species_source_target[source_reaction_reactantID])>1:
                                logging.warning('Multiple matches for '+str(source_reaction_reactantID)+': '+str(species_source_target[source_reaction_reactantID]))
                                logging.warning('Taking one the first one arbitrarely: '+str([i for i in species_source_target[source_reaction_reactantID]][0]))
                            #WARNING: taking the first one arbitrarely
                            rpSBML._checklibSBML(target_reactant.setSpecies(
                                [i for i in species_source_target[source_reaction_reactantID]][0]), 'assign reactant species')
                        else:
                            rpSBML._checklibSBML(target_reactant.setSpecies(source_reaction_reactantID),
                                'assign reactant species')
                    else:
                        rpSBML._checklibSBML(target_reactant.setSpecies(source_reaction_reactantID),
                            'assign reactant species')
                    source_reactant = source_reaction.getReactant(source_reaction_reactantID)
                    rpSBML._checklibSBML(source_reactant, 'fetch source reactant')
                    rpSBML._checklibSBML(target_reactant.setConstant(source_reactant.getConstant()),
                            'set "constant" on species '+str(source_reactant.getConstant()))
                    rpSBML._checklibSBML(target_reactant.setStoichiometry(source_reactant.getStoichiometry()),
                            'set stoichiometry ('+str(source_reactant.getStoichiometry)+')')
                #Products
                logging.debug('Setting products')
                for source_reaction_productID in [i.species for i in source_reaction.getListOfProducts()]:
                    logging.debug('\tAdding '+str(source_reaction_productID))
                    target_product = target_reaction.createProduct()
                    rpSBML._checklibSBML(target_product, 'create target reactant')
                    if source_reaction_productID in species_source_target:
                        if not species_source_target[source_reaction_productID]=={}:
                            if len(species_source_target[source_reaction_reactantID])>1:
                                logging.warning('Multiple matches for '+str(source_reaction_productID)+': '+str(species_source_target[source_reaction_productID]))
                                logging.warning('Taking one arbitrarely')
                            #WARNING: taking the first one arbitrarely
                            rpSBML._checklibSBML(target_product.setSpecies(
                                [i for i in species_source_target[source_reaction_productID]][0]), 'assign reactant product')
                        else:
                            rpSBML._checklibSBML(target_product.setSpecies(source_reaction_productID),
                                'assign reactant product')
                    else:
                        rpSBML._checklibSBML(target_product.setSpecies(source_reaction_productID),
                            'assign reactant product')
                    source_product = source_reaction.getProduct(source_reaction_productID)
                    rpSBML._checklibSBML(source_product, 'fetch source reactant')
                    rpSBML._checklibSBML(target_product.setConstant(source_product.getConstant()),
                            'set "constant" on product '+str(source_product.getConstant()))
                    rpSBML._checklibSBML(target_product.setStoichiometry(source_product.getStoichiometry()),
                            'set stoichiometry ('+str(source_product.getStoichiometry)+')')
        #### GROUPS #####
        #TODO loop through the groups to add them
        if not target_rpsbml.model.isPackageEnabled('groups'):
            rpSBML._checklibSBML(target_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/groups/version1',
                'groups',
                True),
                    'Enabling the GROUPS package')
        #!!!! must be set to false for no apparent reason
        rpSBML._checklibSBML(source_rpsbml.document.setPackageRequired('groups', False), 'enabling groups package')
        source_groups = source_rpsbml.model.getPlugin('groups')
        rpSBML._checklibSBML(source_groups, 'fetching the source model groups')
        target_groups = target_rpsbml.model.getPlugin('groups')
        rpSBML._checklibSBML(target_groups, 'fetching the target model groups')
        #logging.debug('species_source_target: '+str(species_source_target))
        #logging.debug('reac_replace: '+str(reac_replace))
        #TODO: this will overwrite two groups of the same id, need to change
        for group in source_groups.getListOfGroups():
            #for all the species that need to be converted, replace the ones that are
            #if the group is the species group, replace the ones detected from species_source_target
            if group.getId()==species_group_id or group.getId()==sink_species_group_id:
                for member in group.getListOfMembers():
                    if member.getIdRef() in species_source_target:
                        list_species = [i for i in species_source_target[member.getIdRef()]]
                        logging.debug('species_source_target: '+str(species_source_target))
                        logging.debug('list_species: '+str(list_species))
                        if len(list_species)==0:
                            logging.warning('Source species '+str(member.getIdRef())+' has been created in the target model')
                        elif len(list_species)>1:
                            logging.warning('There are multiple matches to the species '+str(member.getIdRef())+'... taking the first one: '+str(list_species))
                            #WARNING: taking the first one arbitrarely
                            member.setIdRef(list_species[0])
                        else:
                            member.setIdRef(list_species[0])
            elif group.getId()==pathway_id:
                for member in group.getListOfMembers():
                    if member.getIdRef() in reac_replace:
                        member.setIdRef(reac_replace[member.getIdRef()])
            rpSBML._checklibSBML(target_groups.addGroup(group),
                    'copy the source groups to the target groups')
        ###### TITLES #####
        target_rpsbml.model.setId(target_rpsbml.model.getId()+'__'+source_rpsbml.model.getId())
        target_rpsbml.model.setName(target_rpsbml.model.getName()+' merged with '+source_rpsbml.model.getId())
        '''
        if fillOrphanSpecies==True:
            self.fillOrphan(target_rpsbml, self.pathway_id, compartment_id)
        '''
        return species_source_target, reac_replace


    @staticmethod
    def _findUniqueRowColumn(pd_matrix):
        logging.debug(pd_matrix)
        to_ret = {}
        ######################## filter by the global top values ################
        logging.debug('################ Filter best #############')
        #transform to np.array
        x = pd_matrix.values
        #resolve the rouding issues to find the max
        x = np.around(x, decimals=5)
        #first round involves finding the highest values and if found set to 0.0 the rows and columns (if unique)
        top = np.where(x==np.max(x))
        #as long as its unique keep looping
        if np.count_nonzero(x)==0:
            return to_ret
        while len(top[0])==1 and len(top[1])==1:
            if np.count_nonzero(x)==0:
                return to_ret
            pd_entry = pd_matrix.iloc[[top[0][0]],[top[1][0]]]
            row_name = str(pd_entry.index[0])
            col_name = str(pd_entry.columns[0])
            if col_name in to_ret:
                logging.debug('Overwriting (1): '+str(col_name))
                logging.debug(x)
            to_ret[col_name] = [row_name]
            #delete the rows and the columns
            logging.debug('==================')
            logging.debug('Column: '+str(col_name))
            logging.debug('Row: '+str(row_name))
            pd_matrix.loc[:, col_name] = 0.0
            pd_matrix.loc[row_name, :] = 0.0
            x = pd_matrix.values
            x = np.around(x, decimals=5)
            top = np.where(x==np.max(x))
            logging.debug(pd_matrix)
            logging.debug(top)
            logging.debug('==================')
        #################### filter by columns (measured) top values ##############
        logging.debug('################ Filter by column best ############')
        x = pd_matrix.values
        x = np.around(x, decimals=5)
        if np.count_nonzero(x)==0:
            return to_ret
        reloop = True
        while reloop:
            if np.count_nonzero(x)==0:
                return to_ret
            reloop = False
            for col in range(len(x[0])):
                if np.count_nonzero(x[:,col])==0:
                    continue
                top_row = np.where(x[:,col]==np.max(x[:,col]))[0]
                if len(top_row)==1:
                    top_row = top_row[0]
                    #if top_row==0.0:
                    #    continue
                    #check to see if any other measured pathways have the same or larger score (accross)
                    row = list(x[top_row, :])
                    #remove current score consideration
                    row.pop(col)
                    if max(row)>=x[top_row, col]:
                        logging.warning('For col '+str(col)+' there are either better or equal values: '+str(row))
                        logging.warning(x)
                        continue
                    #if you perform any changes on the rows and columns, then you can perform the loop again
                    reloop = True
                    pd_entry = pd_matrix.iloc[[top_row],[col]]
                    logging.debug('==================')
                    row_name = pd_entry.index[0]
                    col_name = pd_entry.columns[0]
                    logging.debug('Column: '+str(col_name))
                    logging.debug('Row: '+str(row_name))
                    if col_name in to_ret:
                        logging.debug('Overwriting (2): '+str(col_name))
                        logging.debug(pd_matrix.values)
                    to_ret[col_name] = [row_name]
                    #delete the rows and the columns
                    pd_matrix.loc[:, col_name] = 0.0
                    pd_matrix.loc[row_name, :] = 0.0
                    x = pd_matrix.values
                    x = np.around(x, decimals=5)
                    logging.debug(pd_matrix)
                    logging.debug('==================')
        ################## laslty if there are multiple values that are not 0.0 then account for that ######
        logging.debug('################# get the rest ##########')
        x = pd_matrix.values
        x = np.around(x, decimals=5)
        if np.count_nonzero(x)==0:
            return to_ret
        for col in range(len(x[0])):
            if not np.count_nonzero(x[:,col])==0:
                top_rows = np.where(x[:,col]==np.max(x[:,col]))[0]
                if len(top_rows)==1:
                    top_row = top_rows[0]
                    pd_entry = pd_matrix.iloc[[top_row],[col]]
                    row_name = pd_entry.index[0]
                    col_name = pd_entry.columns[0]
                    if not col_name in to_ret:
                        to_ret[col_name] = [row_name]
                    else:
                        logging.warning('At this point should never have only one: '+str(x[:,col]))
                        logging.warning(x)
                else:
                    for top_row in top_rows:
                        pd_entry = pd_matrix.iloc[[top_row],[col]]
                        row_name = pd_entry.index[0]
                        col_name = pd_entry.columns[0]
                        if not col_name in to_ret:
                            to_ret[col_name] = []
                        to_ret[col_name].append(row_name)
        logging.debug(pd_matrix)
        logging.debug('###################')
        return to_ret

    ##########################################################################################
    #################################### REACTION ############################################
    ##########################################################################################

    ##
    # Compare that all the measured species of a reactions are found within sim species to match with a reaction.
    # We assume that there cannot be two reactions that have the same species and reactants. This is maintained by SBML
    # TODO: need to remove from the list reactions simulated reactions that have matched
    # TODO: Remove. This assumes that reactions can match multiple times, when in fact its impossible
    def compareReactions(species_match, target_rpsbml, source_rpsbml):
        ############## compare the reactions #######################
        #construct sim reactions with species
        logging.debug('------ Comparing reactions --------')
        #match the reactants and products conversion to sim species
        tmp_reaction_match = {}
        source_target = {}
        target_source = {}
        for source_reaction in source_rpsbml.model.getListOfReactions():
            source_reaction_miriam = source_rpsbml.readMIRIAMAnnotation(source_reaction.getAnnotation())
            ################ construct the dict transforming the species #######
            source_target[source_reaction.getId()] = {}
            tmp_reaction_match[source_reaction.getId()] = {}
            for target_reaction in target_rpsbml.model.getListOfReactions():
                if not target_reaction.getId() in target_source:
                    target_source[target_reaction.getId()] = {}
                target_source[target_reaction.getId()][source_reaction.getId()] = {}
                source_target[source_reaction.getId()][target_reaction.getId()] = {}
                logging.debug('\t=========== '+str(target_reaction.getId())+' ==========')
                logging.debug('\t+++++++ Species match +++++++')
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()] = {'reactants': {},
                                                                             'reactants_score': 0.0,
                                                                             'products': {},
                                                                             'products_score': 0.0,
                                                                             'species_score': 0.0,
                                                                             'species_std': 0.0,
                                                                             'species_reaction': None,
                                                                             'ec_score': 0.0,
                                                                             'ec_reaction': None,
                                                                             'score': 0.0,
                                                                             'found': False}
                target_reaction = target_rpsbml.model.getReaction(target_reaction.getId())
                sim_reactants_id = [reactant.species for reactant in target_reaction.getListOfReactants()]
                sim_products_id = [product.species for product in target_reaction.getListOfProducts()]
                ############ species ############
                logging.debug('\tspecies_match: '+str(species_match))
                logging.debug('\tspecies_match: '+str(species_match.keys()))
                logging.debug('\tsim_reactants_id: '+str(sim_reactants_id))
                logging.debug('\tmeasured_reactants_id: '+str([i.species for i in source_reaction.getListOfReactants()]))
                logging.debug('\tsim_products_id: '+str(sim_products_id))
                logging.debug('\tmeasured_products_id: '+str([i.species for i in source_reaction.getListOfProducts()]))
                #ensure that the match is 1:1
                #1)Here we assume that a reaction cannot have twice the same species
                cannotBeSpecies = []
                #if there is a match then we loop again since removing it from the list of potential matches would be appropriate
                keep_going = True
                while keep_going:
                    logging.debug('\t\t----------------------------')
                    keep_going = False
                    for reactant in source_reaction.getListOfReactants():
                        logging.debug('\t\tReactant: '+str(reactant.species))
                        #if a species match has been found AND if such a match has been found
                        founReaIDs = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['id'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'] if not tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['id']==None]
                        logging.debug('\t\tfounReaIDs: '+str(founReaIDs))
                        if reactant.species and reactant.species in species_match and not list(species_match[reactant.species].keys())==[] and not reactant.species in founReaIDs:
                            best_spe = [k for k, v in sorted(species_match[reactant.species].items(), key=lambda item: item[1], reverse=True)][0]
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][reactant.species] = {'id': best_spe, 'score': species_match[reactant.species][best_spe], 'found': True}
                            cannotBeSpecies.append(best_spe)
                        elif not reactant.species in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants']:
                            logging.warning('\t\tCould not find the following measured reactant in the matched species: '+str(reactant.species))
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][reactant.species] = {'id': None, 'score': 0.0, 'found': False}
                    for product in source_reaction.getListOfProducts():
                        logging.debug('\t\tProduct: '+str(product.species))
                        foundProIDs = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['id'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'] if not tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['id']==None]
                        logging.debug('\t\tfoundProIDs: '+str(foundProIDs))
                        if product.species and product.species in species_match and not list(species_match[product.species].keys())==[] and not product.species in foundProIDs:
                            best_spe = [k for k, v in sorted(species_match[product.species].items(), key=lambda item: item[1], reverse=True)][0]
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][product.species] = {'id': best_spe, 'score': species_match[product.species][best_spe], 'found': True}
                            cannotBeSpecies.append(best_spe)
                        elif not product.species in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products']:
                            logging.warning('\t\tCould not find the following measured product in the matched species: '+str(product.species))
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][product.species] = {'id': None, 'score': 0.0, 'found': False}
                    logging.debug('\t\tcannotBeSpecies: '+str(cannotBeSpecies))
                reactants_score = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['score'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants']]
                reactants_found = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['found'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants']]
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants_score'] = np.mean(reactants_score)
                products_score = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['score'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products']]
                products_found = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['found'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products']]
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products_score'] = np.mean(products_score)
                ### calculate pathway species score
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['species_score'] = np.mean(reactants_score+products_score)
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['species_std'] = np.std(reactants_score+products_score)
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['species_reaction'] = target_reaction.getId()
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['found'] = all(reactants_found+products_found)
                tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['score'] = tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['species_score']
                target_source[target_reaction.getId()][source_reaction.getId()] = tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['score']
                source_target[source_reaction.getId()][target_reaction.getId()] = tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['score']
        ### matrix compare #####
        unique = rpSBML._findUniqueRowColumn(pd_DataFrame(source_target))
        logging.debug('findUniqueRowColumn')
        logging.debug(unique)
        reaction_match = {}
        for meas in source_target:
            reaction_match[meas] = {'id': None, 'score': 0.0, 'found': False}
            if meas in unique:
                if len(unique[meas])>1:
                    logging.debug('Multiple values may match, choosing the first arbitrarily: '+str(unique))
                reaction_match[meas]['id'] = unique[meas]
                reaction_match[meas]['score'] = round(tmp_reaction_match[meas][unique[meas][0]]['score'], 5)
                reaction_match[meas]['found'] = tmp_reaction_match[meas][unique[meas][0]]['found']
        #### compile a reaction score based on the ec and species scores
        logging.debug(tmp_reaction_match)
        logging.debug(reaction_match)
        logging.debug('-------------------------------')
        return reaction_match



    ## Compare individual reactions and see if the source reaction is contained within the target one
    #
    # species_source_target: {'MNXM4__64__MNXC3': {'M_o2_c': 1.0}, 'MNXM10__64__MNXC3': {'M_nadh_c': 1.0}, 'CMPD_0000000003__64__MNXC3': {}, 'TARGET_0000000001__64__MNXC3': {}, 'MNXM188__64__MNXC3': {'M_anth_c': 1.0}, 'BC_32877__64__MNXC3': {'M_nh4_c': 0.8}, 'BC_32401__64__MNXC3': {'M_nad_c': 0.2}, 'BC_26705__64__MNXC3': {'M_h_c': 1.0}, 'BC_20662__64__MNXC3': {'M_co2_c': 1.0}}
    # the first keys are the source compartment ids
    # the second key is the source species id
    # the value is the target species id
    # Note that we assure that the match is 1:1 between species using the species match
    #
    #TODO: change this with a flag so that all the reactants and products are the same
    def containedReaction(self, species_source_target, source_reaction, target_reaction):
        scores = []
        all_match = True
        ########### reactants #######
        ignore_reactants = []
        for source_reactant in source_reaction.getListOfReactants():
            if source_reactant.species in species_source_target:
                spe_found = False
                for target_reactiontant in target_reaction.getListOfReactants():
                    if target_reactiontant.species in species_source_target[source_reactant.species] and not target_reactiontant.species in ignore_reactants:
                        scores.append(species_source_target[source_reactant.species][target_reactiontant.species])
                        ignore_reactants.append(target_reactiontant.species)
                        spe_found = True
                        break
                if not spe_found:
                    scores.append(0.0)
                    all_match = False
            else:
                logging.debug('Cannot find the source species '+str(source_reactant.species)+' in the target species: '+str(species_source_target))
                scores.append(0.0)
                all_match = False
        #products
        ignore_products = []
        for source_product in source_reaction.getListOfProducts():
            if source_product.species in species_source_target:
                pro_found = False
                for sim_product in target_reaction.getListOfProducts():
                    if sim_product.species in species_source_target[source_product.species] and not sim_product.species in ignore_products:
                        scores.append(species_source_target[source_product.species][sim_product.species])
                        ignore_products.append(sim_product.species)
                        pro_found = True
                        break
                if not pro_found:
                    scores.append(0.0)
                    all_match = False
            else:
                logging.debug('Cannot find the measured species '+str(source_product.species)+' in the the matched species: '+str(species_source_target))
                scores.append(0.0)
                all_match = False
        return np.mean(scores), all_match




    ## Compare two reactions and elect that they are the same if they have exactly the same reactants and products
    #
    # species_source_target: {'MNXM4__64__MNXC3': {'M_o2_c': 1.0}, 'MNXM10__64__MNXC3': {'M_nadh_c': 1.0}, 'CMPD_0000000003__64__MNXC3': {}, 'TARGET_0000000001__64__MNXC3': {}, 'MNXM188__64__MNXC3': {'M_anth_c': 1.0}, 'BC_32877__64__MNXC3': {'M_nh4_c': 0.8}, 'BC_32401__64__MNXC3': {'M_nad_c': 0.2}, 'BC_26705__64__MNXC3': {'M_h_c': 1.0}, 'BC_20662__64__MNXC3': {'M_co2_c': 1.0}}
    # the first keys are the source compartment ids
    # the second key is the source species id
    # the value is the target species id
    # Note that we assure that the match is 1:1 between species using the species match
    #
    #TODO: change this with a flag so that all the reactants and products are the same
    @staticmethod
    def compareReaction(species_source_target, source_reaction, target_reaction):
        scores = []
        source_reactants = [i.species for i in source_reaction.getListOfReactants()]
        target_reactants = []
        for i in target_reaction.getListOfReactants():
            if i.species in species_source_target:
                if not species_source_target[i.species]=={}:
                    #WARNING: Taking the first one arbitrarely
                    conv_spe = [y for y in species_source_target[i.species]][0]
                    target_reactants.append(conv_spe)
                    scores.append(species_source_target[i.species][conv_spe])
                else:
                    target_reactants.append(i.species)
                    scores.append(1.0)
            else:
                target_reactants.append(i.species)
                scores.append(1.0)
        source_products = [i.species for i in source_reaction.getListOfProducts()]
        target_products = []
        for i in target_reaction.getListOfReactants():
            if i.species in species_source_target:
                if not species_source_target[i.species]=={}:
                    #WARNING: Taking the first one arbitrarely
                    conv_spe = [y for y in species_source_target[i.species]][0]
                    target_products.append(conv_spe)
                    scores.append(species_source_target[i.species][conv_spe])
                else:
                    target_products.append(i.species)
                    scores.append(1.0)
            else:
                target_products.append(i.species)
                scores.append(1.0)
        '''
        logging.debug('source_reactants: '+str(source_reactants))
        logging.debug('target_reactants: '+str(target_reactants))
        logging.debug('source_products: '+str(source_products))
        logging.debug('target_products: '+str(target_products))
        logging.debug(set(source_reactants)-set(target_reactants))
        logging.debug(set(source_products)-set(target_products))
        '''

        if not set(source_reactants)-set(target_reactants) and not set(source_products)-set(target_products):
            return np.mean(scores), True
        else:
            return np.mean(scores), False


    ##########################################################################################
    ##################################### SPECIES ############################################
    ##########################################################################################

    ## Match all the measured chemical species to the simulated chemical species between two SBML
    #
    # TODO: for all the measured species compare with the simualted one. Then find the measured and simulated species that match the best and exclude the
    # simulated species from potentially matching with another
    @staticmethod
    def compareSpecies(comp_source_target, source_rpsbml, target_rpsbml):
        ############## compare species ###################
        source_target = {}
        target_source = {}
        species_match = {}
        for source_species in source_rpsbml.model.getListOfSpecies():
            logging.debug('--- Trying to match chemical species: '+str(source_species.getId())+' ---')
            source_target[source_species.getId()] = {}
            species_match[source_species.getId()] = {}
            #species_match[source_species.getId()] = {'id': None, 'score': 0.0, 'found': False}
            #TODO: need to exclude from the match if a simulated chemical species is already matched with a higher score to another measured species
            for target_species in target_rpsbml.model.getListOfSpecies():
                #skip the species that are not in the same compartment as the source
                if not target_species.getCompartment()==comp_source_target[source_species.getCompartment()]:
                    continue
                source_target[source_species.getId()][target_species.getId()] = {'score': 0.0, 'found': False}
                if not target_species.getId() in target_source:
                    target_source[target_species.getId()] = {}
                target_source[target_species.getId()][source_species.getId()] = {'score': 0.0, 'found': False}
                source_brsynth_annot = target_rpsbml.readBRSYNTHAnnotation(source_species.getAnnotation())
                target_brsynth_annot = target_rpsbml.readBRSYNTHAnnotation(target_species.getAnnotation())
                source_miriam_annot = target_rpsbml.readMIRIAMAnnotation(source_species.getAnnotation())
                target_miriam_annot = target_rpsbml.readMIRIAMAnnotation(target_species.getAnnotation())
                #### MIRIAM ####
                if target_rpsbml.compareMIRIAMAnnotations(source_species.getAnnotation(), target_species.getAnnotation()):
                    logging.debug('--> Matched MIRIAM: '+str(target_species.getId()))
                    source_target[source_species.getId()][target_species.getId()]['score'] += 0.4
                    #source_target[source_species.getId()][target_species.getId()]['score'] += 0.2+0.2*jaccardMIRIAM(target_miriam_annot, source_miriam_annot)
                    source_target[source_species.getId()][target_species.getId()]['found'] = True
                ##### InChIKey ##########
                #find according to the inchikey -- allow partial matches
                #compare either inchikey in brsynth annnotation or MIRIAM annotation
                #NOTE: here we prioritise the BRSynth annotation inchikey over the MIRIAM
                source_inchikey_split = None
                target_inchikey_split = None
                if 'inchikey' in source_brsynth_annot:
                    source_inchikey_split = source_brsynth_annot['inchikey'].split('-')
                elif 'inchikey' in source_miriam_annot:
                    if not len(source_miriam_annot['inchikey'])==1:
                        #TODO: handle mutliple inchikey with mutliple compare and the highest comparison value kept
                        logging.warning('There are multiple inchikey values, taking the first one: '+str(source_miriam_annot['inchikey']))
                    source_inchikey_split = source_miriam_annot['inchikey'][0].split('-')
                if 'inchikey' in target_brsynth_annot:
                    target_inchikey_split = target_brsynth_annot['inchikey'].split('-')
                elif 'inchikey' in target_miriam_annot:
                    if not len(target_miriam_annot['inchikey'])==1:
                        #TODO: handle mutliple inchikey with mutliple compare and the highest comparison value kept
                        logging.warning('There are multiple inchikey values, taking the first one: '+str(target_brsynth_annot['inchikey']))
                    target_inchikey_split = target_miriam_annot['inchikey'][0].split('-')
                if source_inchikey_split and target_inchikey_split:
                    if source_inchikey_split[0]==target_inchikey_split[0]:
                        logging.debug('Matched first layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
                        source_target[source_species.getId()][target_species.getId()]['score'] += 0.2
                        if source_inchikey_split[1]==target_inchikey_split[1]:
                            logging.debug('Matched second layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
                            source_target[source_species.getId()][target_species.getId()]['score'] += 0.2
                            source_target[source_species.getId()][target_species.getId()]['found'] = True
                            if source_inchikey_split[2]==target_inchikey_split[2]:
                                logging.debug('Matched third layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
                                source_target[source_species.getId()][target_species.getId()]['score'] += 0.2
                                source_target[source_species.getId()][target_species.getId()]['found'] = True
                target_source[target_species.getId()][source_species.getId()]['score'] = source_target[source_species.getId()][target_species.getId()]['score']
                target_source[target_species.getId()][source_species.getId()]['found'] = source_target[source_species.getId()][target_species.getId()]['found']
        #build the matrix to send
        source_target_mat = {}
        for i in source_target:
            source_target_mat[i] = {}
            for y in source_target[i]:
                source_target_mat[i][y] = source_target[i][y]['score']
        unique = rpSBML._findUniqueRowColumn(pd_DataFrame(source_target_mat))
        logging.debug('findUniqueRowColumn:')
        logging.debug(unique)
        for meas in source_target:
            if meas in unique:
                species_match[meas] = {}
                for unique_spe in unique[meas]:
                    species_match[meas][unique_spe] = round(source_target[meas][unique[meas][0]]['score'], 5)
            else:
                logging.warning('Cannot find a species match for the measured species: '+str(meas))
        logging.debug('#########################')
        logging.debug('species_match:')
        logging.debug(species_match)
        logging.debug('-----------------------')
        return species_match



    ######################################################################################################################
    ############################################### EC NUMBER ############################################################
    ######################################################################################################################



    def compareEC(meas_reac_miriam, sim_reac_miriam):
        #Warning we only match a single reaction at a time -- assume that there cannot be more than one to match at a given time
        if 'ec-code' in meas_reac_miriam and 'ec-code' in sim_reac_miriam:
            measured_frac_ec = [[y for y in ec.split('.') if not y=='-'] for ec in meas_reac_miriam['ec-code']]
            sim_frac_ec = [[y for y in ec.split('.') if not y=='-'] for ec in sim_reac_miriam['ec-code']]
            #complete the ec numbers with None to be length of 4
            for i in range(len(measured_frac_ec)):
                for y in range(len(measured_frac_ec[i]), 4):
                    measured_frac_ec[i].append(None)
            for i in range(len(sim_frac_ec)):
                for y in range(len(sim_frac_ec[i]), 4):
                    sim_frac_ec[i].append(None)
            logging.debug('Measured: ')
            logging.debug(measured_frac_ec)
            logging.debug('Simulated: ')
            logging.debug(sim_frac_ec)
            best_ec_compare = {'meas_ec': [], 'sim_ec': [], 'score': 0.0, 'found': False}
            for ec_m in measured_frac_ec:
                for ec_s in sim_frac_ec:
                    tmp_score = 0.0
                    for i in range(4):
                        if not ec_m[i]==None and not ec_s[i]==None:
                            if ec_m[i]==ec_s[i]:
                                tmp_score += 0.25
                                if i==2:
                                    best_ec_compare['found'] = True
                            else:
                                break
                    if tmp_score>best_ec_compare['score']:
                        best_ec_compare['meas_ec'] = ec_m
                        best_ec_compare['sim_ec'] = ec_s
                        best_ec_compare['score'] = tmp_score
            return best_ec_compare['score']
        else:
            logging.warning('One of the two reactions does not have any EC entries.\nMeasured: '+str(meas_reac_miriam)+' \nSimulated: '+str(sim_reac_miriam))
            return 0.0





    @staticmethod
    def _search_key(keys, dict):
        for key in keys:
            if key in dict:
                return key


    ## Put species in a dictionnary for further comparison
    #
    # @param pathway rpSBML object
    # @return dict object with species in it
    @staticmethod
    def _normalize_pathway(pathway):

        model = pathway.document.getModel()

        # Get Reactions
        reactions = {}
        for pathway_id in pathway.readRPpathwayIDs('rp_pathway'):
            reaction = model.getReaction(pathway_id)
            reactions[pathway_id] = rpSBML.readBRSYNTHAnnotation(reaction.getAnnotation())

        # Get Species
        species = {}
        for specie in model.getListOfSpecies():
            species[specie.getId()] = rpSBML.readBRSYNTHAnnotation(specie.getAnnotation())

        # Pathways dict
        d_reactions = {}

        keys = ['inchikey', 'inchi', 'smiles']
        # Select Reactions already loaded (w/o Sink one then)
        for reaction in reactions:

            d_reactions[reactions[reaction]['smiles']] = {}

            # Fill the reactants in a dedicated dict
            d_reactants = {}
            for reactant in model.getReaction(reaction).getListOfReactants():#inchikey / inchi sinon miriam sinon IDs
                # Il faut enregistrer toutes les infos (inchi, smiles, id)
                key = rpSBML._search_key(keys, species[reactant.getSpecies()])
                if key: key = species[reactant.getSpecies()][key]
                else:
                    key = reactant.getSpecies()
                d_reactants[key] = reactant.getStoichiometry()
            # Put all reactants dicts in reactions dict for which smiles notations are the keys
            d_reactions[reactions[reaction]['smiles']]['Reactants'] = d_reactants

            # Fill the products in a dedicated dict
            d_products = {}
            for product in model.getReaction(reaction).getListOfProducts():
                key = rpSBML._search_key(keys, species[product.getSpecies()])
                if key: key = species[product.getSpecies()][key]
                else:
                    key = product.getSpecies()
                d_products[key] = product.getStoichiometry()
            # Put all products dicts in reactions dict for which smiles notations are the keys
            d_reactions[reactions[reaction]['smiles']]['Products'] = d_products

        return d_reactions

    def __eq__(self, other):
        return \
            len(self.model.getListOfReactions())==len(other.model.getListOfReactions()) \
        and rpSBML._normalize_pathway(self)==rpSBML._normalize_pathway(other)

    def getScore(self):
        return self.rules_scores[0] / self.rules_scores[1]

    #######################################################################
    ############################# PRIVATE FUNCTIONS #######################
    #######################################################################

    ## Check the libSBML calls
    #
    # Check that the libSBML python calls do not return error INT and if so, display the error. Taken from: http://sbml.org/Software/libSBML/docs/python-api/create_simple_model_8py-example.html
    #
    # @param value The SBML call
    # @param message The string that describes the call
    @staticmethod
    def _checklibSBML(value, message):
        if value is None:
            logging.error('LibSBML returned a null value trying to ' + message + '.')
            raise AttributeError
        elif type(value) is int:
            if value==libsbml.LIBSBML_OPERATION_SUCCESS:
                return
            else:
                err_msg = 'Error encountered trying to ' + message + '.' \
                        + 'LibSBML returned error code ' + str(value) + ': "' \
                        + libsbml.OperationReturnValue_toString(value).strip() + '"'
                logging.error(err_msg)
                raise AttributeError
        else:
            #logging.info(message)
            return None


    ## String to SBML ID
    #
    # Convert any String to one that is compatible with the SBML meta_id formatting requirements
    #
    # @param name The input string
    def _nameToSbmlId(self, name):
        IdStream = []
        count = 0
        end = len(name)
        if '0' <= name[count] and name[count] <= '9':
            IdStream.append('_')
        for count in range(0, end):
            if (('0' <= name[count] and name[count] <= '9') or
                    ('a' <= name[count] and name[count] <= 'z') or
                    ('A' <= name[count] and name[count] <= 'Z')):
                IdStream.append(name[count])
            else:
                IdStream.append('_')
        Id = ''.join(IdStream)
        if Id[len(Id) - 1] != '_':
            return Id
        return Id[:-1]


    ## String to hashed ID
    #
    # Hash an input string and then pass it to _nameToSbmlId()
    #
    # @param input string
    def _genMetaID(self, name):
        return self._nameToSbmlId(sha256(str(name).encode('utf-8')).hexdigest())


    ## compare two dictionarry of lists and return the
    #
    def _compareXref(self, current, toadd):
        toadd = deepcopy(toadd)
        for database_id in current:
            try:
                list_diff = [i for i in toadd[database_id] if i not in current[database_id]]
                if not list_diff:
                    toadd.pop(database_id)
                else:
                    toadd[database_id] = list_diff
            except KeyError:
                pass
        return toadd


    ######################################################################
    ####################### Annotations ##################################
    ######################################################################


    ## Returns a default annotation string
    #
    # @param meta_id String or None Default meta ID
    #
    def _defaultBothAnnot(self, meta_id):
        return '''<annotation>
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
    <rdf:Description rdf:about="#'''+str(meta_id or '')+'''">
      <bqbiol:is>
        <rdf:Bag>
        </rdf:Bag>
      </bqbiol:is>
    </rdf:Description>
    <rdf:BRSynth rdf:about="#'''+str(meta_id or '')+'''">
      <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">
      </brsynth:brsynth>
    </rdf:BRSynth>
  </rdf:RDF>
</annotation>'''


    ## Returns a default annotation string
    #
    # @param meta_id String or None Default meta ID
    #
    def _defaultBRSynthAnnot(self, meta_id):
        return '''<annotation>
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
    <rdf:BRSynth rdf:about="#'''+str(meta_id or '')+'''">
      <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">
      </brsynth:brsynth>
    </rdf:BRSynth>
  </rdf:RDF>
</annotation>'''


    ## Returns a default annotation string
    #
    # @param meta_id String or None Default meta ID
    #
    def _defaultMIRIAMAnnot(self, meta_id):
        return '''<annotation>
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/">
    <rdf:Description rdf:about="#'''+str(meta_id or '')+'''">
      <bqbiol:is>
        <rdf:Bag>
        </rdf:Bag>
      </bqbiol:is>
    </rdf:Description>
  </rdf:RDF>
</annotation>'''



    ## Either add or update the value of a BRSynth annotation
    #
    # @sbase_obj libSBML object that may be compartment, reaction or species
    #
    def addUpdateBRSynth(self, sbase_obj, annot_header, value, units=None, isAlone=False, isList=False, isSort=True, meta_id=None):
        logging.debug('############### '+str(annot_header)+' ################')
        if isList:
            annotation = '''<annotation>
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/" xmlns:bqmodel="http://biomodels.net/model-qualifiers/">
        <rdf:BRSynth rdf:about="#adding">
          <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">
            <brsynth:'''+str(annot_header)+'''>'''
            if isSort:
                for name in sorted(value, key=value.get, reverse=True):
                    if isAlone:
                        annotation += '<brsynth:'+str(name)+'>'+str(value[name])+'</brsynth:'+str(name)+'>'
                    else:
                        if units:
                            annotation += '<brsynth:'+str(name)+' units="'+str(units)+'" value="'+str(value[name])+'" />'
                        else:
                            annotation += '<brsynth:'+str(name)+' value="'+str(value[name])+'" />'
            else:
                for name in value:
                    if isAlone:
                        annotation += '<brsynth:'+str(name)+'>'+str(value[name])+'</brsynth:'+str(name)+'>'
                    else:
                        if units:
                            annotation += '<brsynth:'+str(name)+' units="'+str(units)+'" value="'+str(value[name])+'" />'
                        else:
                            annotation += '<brsynth:'+str(name)+' value="'+str(value[name])+'" />'
            annotation += '''
            </brsynth:'''+str(annot_header)+'''>
          </brsynth:brsynth>
        </rdf:BRSynth>
      </rdf:RDF>
    </annotation>'''
        else:
            #### create the string
            annotation = '''<annotation>
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/" xmlns:bqmodel="http://biomodels.net/model-qualifiers/">
        <rdf:BRSynth rdf:about="#adding">
          <brsynth:brsynth xmlns:brsynth="http://brsynth.eu">'''
            if isAlone:
                annotation += '<brsynth:'+str(annot_header)+'>'+str(value)+'</brsynth:'+str(annot_header)+'>'
            else:
                if units:
                    annotation += '<brsynth:'+str(annot_header)+' units="'+str(units)+'" value="'+str(value)+'" />'
                else:
                    annotation += '<brsynth:'+str(annot_header)+' value="'+str(value)+'" />'
            annotation += '''
          </brsynth:brsynth>
        </rdf:BRSynth>
      </rdf:RDF>
    </annotation>'''
        annot_obj = libsbml.XMLNode.convertStringToXMLNode(annotation)
        if annot_obj==None:
            logging.error('Cannot conver this string to annotation object: '+str(annotation))
            return False
        #### retreive the annotation object
        brsynth_annot = None
        obj_annot = sbase_obj.getAnnotation()
        if not obj_annot:
            sbase_obj.setAnnotation(libsbml.XMLNode.convertStringToXMLNode(self._defaultBRSynthAnnot(meta_id)))
            obj_annot = sbase_obj.getAnnotation()
            if not obj_annot:
                logging.error('Cannot update BRSynth annotation')
                return False
        brsynth_annot = obj_annot.getChild('RDF').getChild('BRSynth').getChild('brsynth')
        if not brsynth_annot:
             logging.error('Cannot find the BRSynth annotation')
             return False
        #add the annotation and replace if it exists
        isfound_target = False
        #logging.debug(brsynth_annot.toXMLString())
        for i in range(brsynth_annot.getNumChildren()):
            logging.debug(annot_header+' -- '+str(brsynth_annot.getChild(i).getName()))
            if annot_header==brsynth_annot.getChild(i).getName():
                isfound_target = True
                '''
                self._checklibSBML(brsynth_annot.removeChild(brsynth_annot.getIndex(i)),
                    'Removing annotation '+str(annot_header))
                '''
                self._checklibSBML(brsynth_annot.removeChild(i), 'Removing annotation '+str(annot_header))
                isfound_source = False
                source_brsynth_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth')
                for y in range(source_brsynth_annot.getNumChildren()):
                    logging.debug('\t'+annot_header+' -- '+str(source_brsynth_annot.getChild(y).getName()))
                    if str(annot_header)==str(source_brsynth_annot.getChild(y).getName()):
                        isfound_source = True
                        logging.debug('Adding annotation to the brsynth annotation: '+str(source_brsynth_annot.getChild(y).toXMLString()))
                        towrite_annot = source_brsynth_annot.getChild(y)
                        logging.debug(brsynth_annot.toXMLString())
                        self._checklibSBML(brsynth_annot.addChild(towrite_annot), ' 1 - Adding annotation to the brsynth annotation')
                        logging.debug(brsynth_annot.toXMLString())
                        break
                if not isfound_source:
                    logging.error('Cannot find '+str(annot_header)+' in source annotation')
        if not isfound_target:
            logging.debug('Cannot find '+str(annot_header)+' in target annotation')
            isfound_source = False
            source_brsynth_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth')
            for y in range(source_brsynth_annot.getNumChildren()):
                logging.debug('\t'+annot_header+' -- '+str(source_brsynth_annot.getChild(y).getName()))
                if str(annot_header)==str(source_brsynth_annot.getChild(y).getName()):
                    isfound_source = True
                    logging.debug('Adding annotation to the brsynth annotation: '+str(source_brsynth_annot.getChild(y).toXMLString()))
                    towrite_annot = source_brsynth_annot.getChild(y)
                    logging.debug(brsynth_annot.toXMLString())
                    self._checklibSBML(brsynth_annot.addChild(towrite_annot), '2 - Adding annotation to the brsynth annotation')
                    logging.debug(brsynth_annot.toXMLString())
                    break
            if not isfound_source:
                logging.error('Cannot find '+str(annot_header)+' in source annotation')
            #toWrite_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth').getChild(annot_header)
            #self._checklibSBML(brsynth_annot.addChild(toWrite_annot), 'Adding annotation to the brsynth annotation')
                return False
        '''
        if brsynth_annot.getChild(annot_header).toXMLString()=='':
            toWrite_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth').getChild(annot_header)
            self._checklibSBML(brsynth_annot.addChild(toWrite_annot), 'Adding annotation to the brsynth annotation')
        else:
            #try:
            logging.debug('==============================')
            found_child = False
            for i in range(brsynth_annot.getNumChildren()):
                if annot_header==brsynth_annot.getChild(i).getName():
                    logging.debug('Found the same name to remove: '+str(annot_header))
                    self._checklibSBML(brsynth_annot.removeChild(brsynth_annot.getIndex(i)),
                        'Removing annotation '+str(annot_header))
                    toWrite_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth').getChild(annot_header)
                    self._checklibSBML(brsynth_annot.addChild(toWrite_annot), 'Adding annotation to the brsynth annotation')
                    found_child = True
                    break
            #cause by a bbug with string lookup
            if not found_child:
                logging.warning('Bug with lookup adding it now: '+str(annot_header))
                toWrite_annot = annot_obj.getChild('RDF').getChild('BRSynth').getChild('brsynth').getChild(annot_header)
                self._checklibSBML(brsynth_annot.addChild(toWrite_annot), 'Adding annotation to the brsynth annotation')
            #except OverflowError:
            #    logging.warning('TODO: Overflow error that must be dealt with')
            #    logging.warning(brsynth_annot.getChild(annot_header).toXMLString())
            #    return False
        '''
        return True

    ## Function to update or create a MIRIAM annotation for a compartment, reaction or species
    #
    # @sbase_obj libSBML object that may be compartment, reaction or species
    # @type_param String Type of MIRIAM to add. May be 'compartment', 'reaction', 'species'
    # @xref type of anno
    #
    def addUpdateMIRIAM(self, sbase_obj, type_param, xref, meta_id=None):
        if not type_param in ['compartment', 'reaction', 'species']:
            logging.error('type_param must be '+str(['compartment', 'reaction', 'species'])+' not '+str(type_param))
            return False
        miriam_annot = None
        isReplace = False
        try:
            miriam_annot = sbase_obj.getAnnotation().getChild('RDF').getChild('Description').getChild('is').getChild('Bag')
            miriam_elements = self.readMIRIAMAnnotation(sbase_obj.getAnnotation())
            if not miriam_elements:
                isReplace = True
                if not meta_id:
                    meta_id = self._genMetaID('tmp_addUpdateMIRIAM')
                miriam_annot_1 = libsbml.XMLNode.convertStringToXMLNode(self._defaultBothAnnot(meta_id))
                miriam_annot = miriam_annot_1.getChild('RDF').getChild('Description').getChild('is').getChild('Bag')
            else:
                miriam_elements = None
        except AttributeError:
            try:
                #Cannot find MIRIAM annotation, create it
                isReplace = True
                if not meta_id:
                    meta_id = self._genMetaID('tmp_addUpdateMIRIAM')
                miriam_annot = libsbml.XMLNode.convertStringToXMLNode(self._defaultMIRIAMAnnot(meta_id))
                miriam_annot = miriam_annot.getChild('RDF').getChild('Description').getChild('is').getChild('Bag')
            except AttributeError:
                logging.error('Fatal error fetching the annotation')
                return False
        #compile the list of current species
        inside = {}
        for i in range(miriam_annot.getNumChildren()):
            single_miriam = miriam_annot.getChild(i)
            if single_miriam.getAttributes().getLength()>1:
                logging.error('MIRIAM annotations should never have more than 1: '+str(single_miriam.toXMLString()))
                continue
            single_miriam_attr = single_miriam.getAttributes()
            if not single_miriam_attr.isEmpty():
                try:
                    db = single_miriam_attr.getValue(0).split('/')[-2]
                    v = single_miriam_attr.getValue(0).split('/')[-1]
                    inside[self.header_miriam[type_param][db]].append(v)
                except KeyError:
                    try:
                        db = single_miriam_attr.getValue(0).split('/')[-2]
                        v = single_miriam_attr.getValue(0).split('/')[-1]
                        inside[self.header_miriam[type_param][db]] = [v]
                    except KeyError:
                        logging.warning('Cannot find the self.header_miriram entry '+str(db))
                        continue
            else:
                logging.warning('Cannot return MIRIAM attribute')
                pass
        #add or ignore
        toadd = self._compareXref(inside, xref)
        for database_id in toadd:
            for species_id in toadd[database_id]:
                #not sure how to avoid having it that way
                if database_id in self.miriam_header[type_param]:
                    try:
                        #determine if the dictionnaries
                        annotation = '''<annotation>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/" xmlns:bqmodel="http://biomodels.net/model-qualifiers/">
    <rdf:Description rdf:about="#tmp">
      <bqbiol:is>
        <rdf:Bag>'''
                        if type_param=='species':
                            if database_id=='kegg' and species_id[0]=='C':
                                annotation += '''
              <rdf:li rdf:resource="http://identifiers.org/'''+self.miriam_header[type_param]['kegg_c']+str(species_id)+'''"/>'''
                            elif database_id=='kegg' and species_id[0]=='D':
                                annotation += '''
              <rdf:li rdf:resource="http://identifiers.org/'''+self.miriam_header[type_param]['kegg_d']+str(species_id)+'''"/>'''
                            else:
                                annotation += '''
              <rdf:li rdf:resource="http://identifiers.org/'''+self.miriam_header[type_param][database_id]+str(species_id)+'''"/>'''
                        else:
                            annotation += '''
              <rdf:li rdf:resource="http://identifiers.org/'''+self.miriam_header[type_param][database_id]+str(species_id)+'''"/>'''
                        annotation += '''
        </rdf:Bag>
      </bqbiol:is>
    </rdf:Description>
    </rdf:RDF>
    </annotation>'''
                        toPass_annot = libsbml.XMLNode.convertStringToXMLNode(annotation)
                        toWrite_annot = toPass_annot.getChild('RDF').getChild('Description').getChild('is').getChild('Bag').getChild(0)
                        miriam_annot.insertChild(0, toWrite_annot)
                    except KeyError:
                        #WARNING need to check this
                        logging.warning('Cannot find '+str(database_id)+' in self.miriam_header for '+str(type_param))
                        continue
        if isReplace:
            ori_miriam_annot = sbase_obj.getAnnotation()
            if ori_miriam_annot==None:
                sbase_obj.unsetAnnotation()
                sbase_obj.setAnnotation(miriam_annot)
            else:
                rpSBML._checklibSBML(ori_miriam_annot.getChild('RDF').getChild('Description').getChild('is').removeChild(0), 'Removing annotation "is"')
                rpSBML._checklibSBML(ori_miriam_annot.getChild('RDF').getChild('Description').getChild('is').addChild(miriam_annot), 'Adding annotation to the brsynth annotation')
        return True

    ## Generate in-house json output of the rpSBML model including the annotations for the BRSynth and MIRIAM
    #
    #
    # TODO: change the name of the function to: rpJSON
    def genJSON(self, pathway_id='rp_pathway'):
        groups = self.model.getPlugin('groups')
        rp_pathway = groups.getGroup(pathway_id)
        reactions = rp_pathway.getListOfMembers()
        #pathway
        rpsbml_json = {}
        rpsbml_json['pathway'] = {}
        rpsbml_json['pathway']['brsynth'] = self.readBRSYNTHAnnotation(rp_pathway.getAnnotation())
        #reactions
        rpsbml_json['reactions'] = {}
        for member in reactions:
            reaction = self.model.getReaction(member.getIdRef())
            annot = reaction.getAnnotation()
            rpsbml_json['reactions'][member.getIdRef()] = {}
            rpsbml_json['reactions'][member.getIdRef()]['brsynth'] = self.readBRSYNTHAnnotation(annot)
            rpsbml_json['reactions'][member.getIdRef()]['miriam'] = self.readMIRIAMAnnotation(annot)
        #loop though all the species
        rpsbml_json['species'] = {}
        for spe_id in self.readUniqueRPspecies(pathway_id):
            species = self.model.getSpecies(spe_id)
            annot = species.getAnnotation()
            rpsbml_json['species'][spe_id] = {}
            rpsbml_json['species'][spe_id]['brsynth'] = self.readBRSYNTHAnnotation(annot)
            rpsbml_json['species'][spe_id]['miriam'] = self.readMIRIAMAnnotation(annot)
        return rpsbml_json


    #####################################################################
    ########################## INPUT/OUTPUT #############################
    #####################################################################


    ## Open an SBML using libSBML
    #
    # Situation where an SBML is passed to add the heterologous pathway
    #
    # @param inFile String Path to the input SBML file
    def readSBML(self, inFile):
        if not os_path.isfile(inFile):
            logging.error('Invalid input file')
            raise FileNotFoundError
        document = libsbml.readSBMLFromFile(inFile)
        rpSBML._checklibSBML(document, 'reading input file')
        errors = document.getNumErrors()
        #display the errors in the log accordning to the severity
        for err in [document.getError(i) for i in range(document.getNumErrors())]:
            #TODO if the error is related to packages not enabled (like groups or fbc) activate them
            if err.isFatal:
                logging.error('libSBML reading error: '+str(err.getShortMessage()))
                raise FileNotFoundError
            else:
                logging.warning('libSBML reading warning: '+str(err.getShortMessage()))
        model = document.getModel()
        if not model:
            logging.error('Either the file was not read correctly or the SBML is empty')
            raise FileNotFoundError
        self.document = document
        self.model = model
        #enabling the extra packages if they do not exists when reading a model
        if not self.model.isPackageEnabled('groups'):
            rpSBML._checklibSBML(self.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/groups/version1',
                'groups',
                True),
                    'Enabling the GROUPS package')
            rpSBML._checklibSBML(self.document.setPackageRequired('groups', False), 'enabling groups package')
        if not self.model.isPackageEnabled('fbc'):
            rpSBML._checklibSBML(self.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/fbc/version2',
                'fbc',
                True),
                    'Enabling the FBC package')
            rpSBML._checklibSBML(self.document.setPackageRequired('fbc', False), 'enabling FBC package')


    ## Export a libSBML model to file
    #
    # Export the libSBML model to an SBML file
    #
    # @param model libSBML model to be saved to file
    # @param model_id model id, note that the name of the file will be that
    # @param path Non required parameter that will define the path where the model will be saved
    def writeSBML(self, path):
        ####### check the path #########
        #need to determine where are the path id's coming from
        p = None
        if path:
            if path[-1:]=='/':
                path = path[:-1]
            if not os_path.isdir(path):
                if self.path:
                    p = self.path
                else:
                    logging.error('The output path is not a directory: '+str(path))
                    return False
            else:
                p = path
        else:
            p = self.path

        ########## check and create folder #####
        if not os_path.exists(p):
            os_mkdirs(p)
        ext = ''
        if not str(self.modelName).endswith('_sbml'):
            ext = '_sbml'
        libsbml.writeSBMLToFile(self.document, p+'/'+str(self.modelName)+ext+'.xml')
        return True


    #####################################################################
    ########################## FindCreate ###############################
    #####################################################################


    ## Find the objective (with only one reaction associated) based on the reaction ID and if not found create it
    #
    #
    #
    def findCreateObjective(self, reactions, coefficients, isMax=True, objective_id=None):
        fbc_plugin = self.model.getPlugin('fbc')
        rpSBML._checklibSBML(fbc_plugin, 'Getting FBC package')
        if not objective_id:
            objective_id = 'obj_'+'_'.join(reactions)
            logging.info('Setting objective as '+str(objective_id))
        for objective in fbc_plugin.getListOfObjectives():
            if objective.getId()==objective_id:
                logging.warning('The specified objective id ('+str(objective_id)+') already exists')
                return objective_id
            if not set([i.getReaction() for i in objective.getListOfFluxObjectives()])-set(reactions):
                #TODO: consider setting changing the name of the objective
                logging.warning('The specified objective id ('+str(objective_id)+') has another objective with the same reactions: '+str(objective.getId()))
                return objective.getId()
        #If cannot find a valid objective create it
        self.createMultiFluxObj(objective_id,
                                reactions,
                                coefficients,
                                isMax)
        return objective_id


    #####################################################################
    ########################## READ #####################################
    #####################################################################


    ## Return the reaction ID's and the pathway annotation
    #
    # TODO: replace the name of this function with readRPpathwayIDs
    def readRPpathwayIDs(self, pathway_id='rp_pathway'):
        groups = self.model.getPlugin('groups')
        rp_pathway = groups.getGroup(pathway_id)
        rpSBML._checklibSBML(rp_pathway, 'retreiving groups rp_pathway')
        toRet = []
        for member in rp_pathway.getListOfMembers():
            toRet.append(member.getIdRef())
        return toRet


    ## Read the reaction rules from the BRSYNTH annotation
    #
    #@param pathway_id default='rp_pathway' unique ID (per SBML) where the heterologous pathways are stored
    #@return toRet dictionnary with the reaction rule and rule_id as key
    def readRPrules(self, pathway_id='rp_pathway'):
        toRet = {}
        for reacId in self.readRPpathwayIDs(pathway_id):
            reac = self.model.getReaction(reacId)
            brsynth_annot = self.readBRSYNTHAnnotation(reac.getAnnotation())
            if not brsynth_annot['rule_id']=='' and not brsynth_annot['smiles']=='':
                toRet[brsynth_annot['rule_id']] = brsynth_annot['smiles'].replace('&gt;', '>')
        return toRet


    ## Return the species annitations
    #
    #
    def readRPspecies(self, pathway_id='rp_pathway'):
        reacMembers = {}
        for reacId in self.readRPpathwayIDs(pathway_id):
            reacMembers[reacId] = {}
            reacMembers[reacId]['products'] = {}
            reacMembers[reacId]['reactants'] = {}
            reac = self.model.getReaction(reacId)
            for pro in reac.getListOfProducts():
                reacMembers[reacId]['products'][pro.getSpecies()] = pro.getStoichiometry()
            for rea in reac.getListOfReactants():
                reacMembers[reacId]['reactants'][rea.getSpecies()] = rea.getStoichiometry()
        return reacMembers


    ## Return the species
    #
    #
    def readUniqueRPspecies(self, pathway_id='rp_pathway'):
        rpSpecies = self.readRPspecies()
        toRet = []
        for i in rpSpecies:
            for y in rpSpecies[i]:
                for z in rpSpecies[i][y]:
                    if not z in toRet:
                        toRet.append(z)
        return toRet
        #reacMembers = self.readRPspecies(pathway_id)
        #return set(set(ori_rp_path['products'].keys())|set(ori_rp_path['reactants'].keys()))


    ## Return the Taxonomy ID from an annotation
    #
    #
    def readTaxonAnnotation(self, annot):
        try:
            toRet = {}
            bag = annot.getChild('RDF').getChild('Description').getChild('hasTaxon').getChild('Bag')
            for i in range(bag.getNumChildren()):
                str_annot = bag.getChild(i).getAttrValue(0)
                if str_annot=='':
                    logging.warning('This contains no attributes: '+str(bag.getChild(i).toXMLString()))
                    continue
                dbid = str_annot.split('/')[-2].split('.')[0]
                if len(str_annot.split('/')[-1].split(':'))==2:
                    cid = str_annot.split('/')[-1].split(':')[1]
                else:
                    cid = str_annot.split('/')[-1]
                if not dbid in toRet:
                    toRet[dbid] = []
                toRet[dbid].append(cid)
            return toRet
        except AttributeError:
            return {}


    ## Return the MIRIAM annotations of species
    #
    #
    def readMIRIAMAnnotation(self, annot):
        try:
            toRet = {}
            bag = annot.getChild('RDF').getChild('Description').getChild('is').getChild('Bag')
            for i in range(bag.getNumChildren()):
                str_annot = bag.getChild(i).getAttrValue(0)
                if str_annot=='':
                    logging.warning('This contains no attributes: '+str(bag.getChild(i).toXMLString()))
                    continue
                dbid = str_annot.split('/')[-2].split('.')[0]
                if len(str_annot.split('/')[-1].split(':'))==2:
                    cid = str_annot.split('/')[-1].split(':')[1]
                else:
                    cid = str_annot.split('/')[-1]
                if not dbid in toRet:
                    toRet[dbid] = []
                toRet[dbid].append(cid)
            return toRet
        except AttributeError:
            return {}


    ## Takes for input a libSBML annotatio object and returns a dictionnary of the annotations
    #
    @staticmethod
    def readBRSYNTHAnnotation(annot):
        toRet = {'dfG_prime_m': {},
                 'dfG_uncert': {},
                 'dfG_prime_o': {},
                 'path_id': None,
                 'step_id': None,
                 'sub_step_id': None,
                 'rule_score': None,
                 'smiles': None,
                 'inchi': None,
                 'inchikey': None,
                 'selenzyme': None,
                 'rule_id': None,
                 'rule_ori_reac': None,
                 'rule_score': None,
                 'global_score': None}
        if annot==None:
            logging.warning('The passed annotation is None')
            return {}
        bag = annot.getChild('RDF').getChild('BRSynth').getChild('brsynth')
        for i in range(bag.getNumChildren()):
            ann = bag.getChild(i)
            if ann=='':
                # logging.warning('This contains no attributes: '+str(ann.toXMLString()))
                #@Joan: There is a reason why there is a print here (and below) and not logging?
                print('This contains no attributes: '+str(ann.toXMLString()))
                continue
            if ann.getName()=='dfG_prime_m' or ann.getName()=='dfG_uncert' or ann.getName()=='dfG_prime_o' or ann.getName()[0:4]=='fba_' or ann.getName()=='flux_value':
                try:
                    toRet[ann.getName()] = {
                            'units': ann.getAttrValue('units'),
                            'value': float(ann.getAttrValue('value'))}
                except ValueError:
                    # logging.warning('Cannot interpret '+str(ann.getName())+': '+str(ann.getAttrValue('value')+' - '+str(ann.getAttrValue('units'))))
                    print('Cannot interpret '+str(ann.getName())+': '+str(ann.getAttrValue('value')+' - '+str(ann.getAttrValue('units'))))
                    toRet[ann.getName()] = {
                            'units': None,
                            'value': None}
            elif ann.getName()=='path_id' or ann.getName()=='step_id' or ann.getName()=='sub_step_id':
                try:
                    #toRet[ann.getName()] = int(ann.getAttrValue('value'))
                    toRet[ann.getName()] = {'value': int(ann.getAttrValue('value'))}
                except ValueError:
                    toRet[ann.getName()] = None
            elif ann.getName()=='rule_score' or ann.getName()=='global_score' or ann.getName()[:5]=='norm_':
                try:
                    #toRet[ann.getName()] = float(ann.getAttrValue('value'))
                    toRet[ann.getName()] = {'value': float(ann.getAttrValue('value'))}
                except ValueError:
                    toRet[ann.getName()] = None
            elif ann.getName()=='smiles':
                toRet[ann.getName()] = ann.getChild(0).toXMLString().replace('&gt;', '>')
            #lists in the annotation
            #The below is for the pre-new rules organisation of the SBML files
            #elif ann.getName()=='selenzyme' or ann.getName()=='rule_ori_reac':
            elif ann.getName()=='selenzyme':
                toRet[ann.getName()] = {}
                for y in range(ann.getNumChildren()):
                    selAnn = ann.getChild(y)
                    try:
                        toRet[ann.getName()][selAnn.getName()] = float(selAnn.getAttrValue('value'))
                    except ValueError:
                        toRet[ann.getName()][selAnn.getName()] = selAnn.getAttrValue('value')
            else:
                toRet[ann.getName()] = ann.getChild(0).toXMLString()
        #to delete empty
        return {k: v for k, v in toRet.items() if v is not None}
        #return toRet


    ## Function to return the products and the species associated with a reaction
    # TODO: delete
    # @return Dictionnary with right==product and left==reactants
    def readReactionSpecies_old(self, reaction, isID=False):
        #TODO: check that reaction is either an sbml species; if not check that its a string and that
        # it exists in the rpsbml model
        toRet = {'left': {}, 'right': {}}
        #reactants
        for i in range(reaction.getNumReactants()):
            reactant_ref = reaction.getReactant(i)
            reactant = self.model.getSpecies(reactant_ref.getSpecies())
            if isID:
                toRet['left'][reactant.getId()] = int(reactant_ref.getStoichiometry())
            else:
                toRet['left'][reactant.getName()] = int(reactant_ref.getStoichiometry())
        #products
        for i in range(reaction.getNumProducts()):
            product_ref = reaction.getProduct(i)
            product = self.model.getSpecies(product_ref.getSpecies())
            if isID:
                toRet['right'][product.getId()] = int(product_ref.getStoichiometry())
            else:
                toRet['right'][product.getName()] = int(product_ref.getStoichiometry())
            toRet['reversible'] = reaction.getReversible()
        return toRet


    ## Function to return the products and the species associated with a reaction
    #
    # @return Dictionnary with right==product and left==reactants
    def readReactionSpecies(self, reaction):
        #TODO: check that reaction is either an sbml species; if not check that its a string and that
        # it exists in the rpsbml model
        toRet = {'left': {}, 'right': {}}
        #reactants
        for i in range(reaction.getNumReactants()):
            reactant_ref = reaction.getReactant(i)
            toRet['left'][reactant_ref.getSpecies()] = int(reactant_ref.getStoichiometry())
        #products
        for i in range(reaction.getNumProducts()):
            product_ref = reaction.getProduct(i)
            toRet['right'][product_ref.getSpecies()] = int(product_ref.getStoichiometry())
        return toRet


    #####################################################################
    ######################### INQUIRE ###################################
    #####################################################################


    ## Function to find out if the model already contains a species according to its ID
    #
    #
    def speciesExists(self, speciesName, compartment_id='MNXC3'):
        if speciesName in [i.getName() for i in self.model.getListOfSpecies()] or speciesName+'__64__'+compartment_id in [i.getId() for i in self.model.getListOfSpecies()]:
            return True
        return False


    ## Function to determine if a species CAN be a product of any reaction.
    #
    # Note that this is only determines if a species can possibly be produced, but does not
    # guarantee it
    #
    # @param species_id String ID of the species
    # @param ignoreReactions List Default is empty, ignore specific reactions
    def isSpeciesProduct(self, species_id, ignoreReactions=[]):
        #return all the parameters values
        param_dict = {i.getId(): i.getValue() for i in self.model.parameters}
        for reaction in self.model.getListOfReactions():
            if reaction.getId() not in ignoreReactions:
                #check that the function is reversible by reversibility and FBC bounds
                if reaction.reversible:
                    reaction_fbc = reaction.getPlugin('fbc')
                    #strict left to right
                    if param_dict[reaction_fbc.getLowerFluxBound()]>=0 and param_dict[reaction_fbc.getUpperFluxBound()]>0:
                        if species_id in [i.getSpecies() for i in reaction.getListOfProducts()]:
                            return True
                    #can go both ways
                    elif param_dict[reaction_fbc.getLowerFluxBound()]<0 and param_dict[reaction_fbc.getUpperFluxBound()]>0:
                        if species_id in [i.getSpecies() for i in reaction.getListOfProducts()]:
                            return True
                        elif species_id in [i.getSpecies() for i in reaction.getListOfReactants()]:
                            return True
                    #strict right to left
                    elif param_dict[reaction_fbc.getLowerFluxBound()]<0 and param_dict[reaction_fbc.getUpperFluxBound()]<=0 and param_dict[reaction_fbc.getLowerFluxBound()]<param_dict[reaction_fbc.getUpperFluxBound()]:
                        if species_id in [i.getSpecies() for i in reaction.getListOfReactants()]:
                            return True
                    else:
                        logging.warning('isSpeciesProduct does not find the directionailty of the reaction for reaction: '+str(species_id))
                        return True
                else:
                    #if the reaction is not reversible then product are the only way to create it
                    if species_id in [i.getSpecies() for i in reaction.getListOfProducts()]:
                        return True
        return False


    #########################################################################
    ################### CONVERT BETWEEEN FORMATS ############################
    #########################################################################


    ## Really used to complete the monocomponent reactions
    #{'rule_id': 'RR-01-503dbb54cf91-49-F', 'right': {'TARGET_0000000001': 1}, 'left': {'MNXM2': 1, 'MNXM376': 1}, 'pathway_id': 1, 'step': 1, 'sub_step': 1, 'transformation_id': 'TRS_0_0_17'}
    #
    def outPathsDict(self, pathway_id='rp_pathway'):
        pathway = {}
        for member in self.readRPpathwayIDs(pathway_id):
            #TODO: need to find a better way
            reaction = self.model.getReaction(member)
            brsynthAnnot = self.readBRSYNTHAnnotation(reaction.getAnnotation())
            speciesReac = self.readReactionSpecies(reaction)
            step = {'reaction_id': member,
                    'reaction_rule': brsynthAnnot['smiles'],
                    'rule_score': brsynthAnnot['rule_score'],
                    'rule_id': brsynthAnnot['rule_id'],
                    'rule_ori_reac': brsynthAnnot['rule_ori_reac'],
                    'right': speciesReac['right'],
                    'left': speciesReac['left'],
                    'path_id': brsynthAnnot['path_id'],
                    'step': brsynthAnnot['step_id'],
                    'sub_step': brsynthAnnot['sub_step_id']}
            pathway[brsynthAnnot['step_id']['value']] = step
        return pathway


    #########################################################################
    ############################# COMPARE MODELS ############################
    #########################################################################


    ## Find out if two libSBML Species or Reactions come from the same species
    #
    # Compare two dictionnaries and if any of the values of any of the same keys are the same then the
    # function return True, and if none are found then return False
    #
    # @param libSBML Annotation object for one of the
    # @return Boolean to determine if they are the same
    def compareBRSYNTHAnnotations(self, source_annot, target_annot):
        source_dict = self.readBRSYNTHAnnotation(source_annot)
        target_dict = self.readBRSYNTHAnnotation(target_annot)
        #ignore thse when comparing reactions
        for i in ['path_id', 'step', 'sub_step', 'rule_score', 'rule_ori_reac']:
            try:
                del source_dict[i]
            except KeyError:
                pass
            try:
                del target_dict[i]
            except KeyError:
                pass
        #list the common keys between the two
        for same_key in list(set(list(source_dict.keys())).intersection(list(target_dict.keys()))):
            if source_dict[same_key]==target_dict[same_key]:
                return True
        return False


    ## Find out if two libSBML Species or Reactions come from the same species
    #
    # Compare two dictionnaries and if any of the values of any of the same keys are the same then the
    # function return True, and if none are found then return False
    #
    # @param libSBML Annotation object for one of the
    # @return Boolean to determine if they are the same
    def compareMIRIAMAnnotations(self, source_annot, target_annot):
        source_dict = self.readMIRIAMAnnotation(source_annot)
        target_dict = self.readMIRIAMAnnotation(target_annot)
        #list the common keys between the two
        for com_key in set(list(source_dict.keys()))-(set(list(source_dict.keys()))-set(list(target_dict.keys()))):
            #compare the keys and if same is non-empty means that there
            #are at least one instance of the key that is the same
            if bool(set(source_dict[com_key]) & set(target_dict[com_key])):
                return True
        return False


    ## Compare an annotation and a dictionnary structured
    #
    #
    def compareAnnotations_annot_dict(self, source_annot, target_dict):
        source_dict = self.readMIRIAMAnnotation(source_annot)
        #list the common keys between the two
        for com_key in set(list(source_dict.keys()))-(set(list(source_dict.keys()))-set(list(target_dict.keys()))):
            #compare the keys and if same is non-empty means that there
            #are at least one instance of the key that is the same
            if bool(set(source_dict[com_key]) & set(target_dict[com_key])):
                return True
        return False


    ## Compare two dictionnaries sutructured as dict
    #
    #
    def compareAnnotations_dict_dict(self, source_dict, target_dict):
        #list the common keys between the two
        for com_key in set(list(source_dict.keys()))-(set(list(source_dict.keys()))-set(list(target_dict.keys()))):
            #compare the keys and if same is non-empty means that there
            #are at least one instance of the key that is the same
            if bool(set(source_dict[com_key]) & set(target_dict[com_key])):
                return True
        return False


    ## Function to compare two SBML's RP pathways
    #
    # Function that compares the annotations of reactions and if not found, the annotations of all
    # species in that reaction to try to recover the correct ones. Because we are working with
    # intermediate cofactors for the RP generated pathways, the annotation crossreference will
    # not work. Best is to use the cross-reference to the original reaction
    #
    def compareRPpathways(self, measured_sbml):
        #return all the species annotations of the RP pathways
        try:
            meas_rp_species = measured_sbml.readRPspecies()
            found_meas_rp_species = measured_sbml.readRPspecies()
            for meas_step_id in meas_rp_species:
                meas_rp_species[meas_step_id]['annotation'] = measured_sbml.model.getReaction(meas_step_id).getAnnotation()
                found_meas_rp_species[meas_step_id]['found'] = False
                for spe_name in meas_rp_species[meas_step_id]['reactants']:
                    meas_rp_species[meas_step_id]['reactants'][spe_name] = measured_sbml.model.getSpecies(spe_name).getAnnotation()
                    found_meas_rp_species[meas_step_id]['reactants'][spe_name] = False
                for spe_name in meas_rp_species[meas_step_id]['products']:
                    meas_rp_species[meas_step_id]['products'][spe_name] = measured_sbml.model.getSpecies(spe_name).getAnnotation()
                    found_meas_rp_species[meas_step_id]['products'][spe_name] = False
            rp_rp_species = self.readRPspecies()
            for rp_step_id in rp_rp_species:
                rp_rp_species[rp_step_id]['annotation'] = self.model.getReaction(rp_step_id).getAnnotation()
                for spe_name in rp_rp_species[rp_step_id]['reactants']:
                    rp_rp_species[rp_step_id]['reactants'][spe_name] = self.model.getSpecies(spe_name).getAnnotation()
                for spe_name in rp_rp_species[rp_step_id]['products']:
                    rp_rp_species[rp_step_id]['products'][spe_name] = self.model.getSpecies(spe_name).getAnnotation()
        except AttributeError:
            logging.error('TODO: debug, for some reason some are passed as None here')
            return False, {}
        #compare the number of steps in the pathway
        if not len(meas_rp_species)==len(rp_rp_species):
            logging.warning('The pathways are not of the same length')
            return False, {}
        ############## compare using the reactions ###################
        for meas_step_id in measured_sbml.readRPpathwayIDs():
            for rp_step_id in rp_rp_species:
                if self.compareMIRIAMAnnotations(rp_rp_species[rp_step_id]['annotation'], meas_rp_species[meas_step_id]['annotation']):
                    found_meas_rp_species[meas_step_id]['found'] = True
                    found_meas_rp_species[meas_step_id]['rp_step_id'] = rp_step_id
                    break
        ############## compare using the species ###################
        for meas_step_id in measured_sbml.readRPpathwayIDs():
            #if not found_meas_rp_species[meas_step_id]['found']:
            for rp_step_id in rp_rp_species:
                # We test to see if the meas reaction elements all exist in rp reaction and not the opposite
                #because the measured pathways may not contain all the elements
                ########## reactants ##########
                for meas_spe_id in meas_rp_species[meas_step_id]['reactants']:
                    for rp_spe_id in rp_rp_species[rp_step_id]['reactants']:
                        if self.compareMIRIAMAnnotations(meas_rp_species[meas_step_id]['reactants'][meas_spe_id], rp_rp_species[rp_step_id]['reactants'][rp_spe_id]):
                            found_meas_rp_species[meas_step_id]['reactants'][meas_spe_id] = True
                            break
                        else:
                            if self.compareBRSYNTHAnnotations(meas_rp_species[meas_step_id]['reactants'][meas_spe_id], rp_rp_species[rp_step_id]['reactants'][rp_spe_id]):
                                found_meas_rp_species[meas_step_id]['reactants'][meas_spe_id] = True
                                break
                ########### products ###########
                for meas_spe_id in meas_rp_species[meas_step_id]['products']:
                    for rp_spe_id in rp_rp_species[rp_step_id]['products']:
                        if self.compareMIRIAMAnnotations(meas_rp_species[meas_step_id]['products'][meas_spe_id], rp_rp_species[rp_step_id]['products'][rp_spe_id]):
                            found_meas_rp_species[meas_step_id]['products'][meas_spe_id] = True
                            break
                        else:
                            if self.compareBRSYNTHAnnotations(meas_rp_species[meas_step_id]['products'][meas_spe_id], rp_rp_species[rp_step_id]['products'][rp_spe_id]):
                                found_meas_rp_species[meas_step_id]['products'][meas_spe_id] = True
                                break
                ######### test to see the difference
                pro_found = [found_meas_rp_species[meas_step_id]['products'][i] for i in found_meas_rp_species[meas_step_id]['products']]
                rea_found = [found_meas_rp_species[meas_step_id]['reactants'][i] for i in found_meas_rp_species[meas_step_id]['reactants']]
                if pro_found and rea_found:
                    if all(pro_found) and all(rea_found):
                        found_meas_rp_species[meas_step_id]['found'] = True
                        found_meas_rp_species[meas_step_id]['rp_step_id'] = rp_step_id
                        break
        ################# Now see if all steps have been found ############
        if all(found_meas_rp_species[i]['found'] for i in found_meas_rp_species):
            found_meas_rp_species['measured_model_id'] = measured_sbml.model.getId()
            found_meas_rp_species['rp_model_id'] = self.model.getId()
            return True, found_meas_rp_species
        else:
            return False, {}


    #########################################################################
    ############################# MODEL APPEND ##############################
    #########################################################################


    ## Set a given reaction's upper and lower bounds
    #
    # Sets the upper and lower bounds of a reaction. Note that if the numerical values passed
    # are not recognised, new parameters are created for each of them
    #
    def setReactionConstraints(self,
                               reaction_id,
                               upper_bound,
                               lower_bound,
                               unit='mmol_per_gDW_per_hr',
                               is_constant=True):
        reaction = self.model.getReaction(reaction_id)
        if not reaction:
            logging.error('Cannot find the reaction: '+str(reaction_id))
            return False
        reac_fbc = reaction.getPlugin('fbc')
        rpSBML._checklibSBML(reac_fbc, 'extending reaction for FBC')
        ########## upper bound #############
        old_upper_value = self.model.getParameter(reac_fbc.getUpperFluxBound()).value
        upper_param = self.createReturnFluxParameter(upper_bound, unit, is_constant)
        rpSBML._checklibSBML(reac_fbc.setUpperFluxBound(upper_param.getId()),
            'setting '+str(reaction_id)+' upper flux bound')
        ######### lower bound #############
        old_lower_value = self.model.getParameter(reac_fbc.getLowerFluxBound()).value
        lower_param = self.createReturnFluxParameter(lower_bound, unit, is_constant)
        rpSBML._checklibSBML(reac_fbc.setLowerFluxBound(lower_param.getId()),
            'setting '+str(reaction_id)+' lower flux bound')
        return old_upper_value, old_lower_value


    ##### ADD SOURCE FROM ORPHAN #####
    #if the heterologous pathway from the self.model contains a sink molecule that is not included in the
    # original model (we call orhpan species) then add another reaction that creates it
    #TODO: that transports the reactions that creates the species in the
    # extracellular matrix and another reaction that transports it from the extracellular matrix to the cytoplasm
    #TODO: does not work
    def fillOrphan(self,
            rpsbml=None,
            pathway_id='rp_pathway',
            compartment_id='MNXC3',
            upper_flux_bound=999999,
            lower_flux_bound=10):
        if rpsbml==None:
            model = self.model
        else:
            model = rpsbml.model
        logging.info('Adding the orphan species to the GEM model')
        #only for rp species
        groups = model.getPlugin('groups')
        rp_pathway = groups.getGroup(pathway_id)
        reaction_id = sorted([(int(''.join(x for x in i.id_ref if x.isdigit())), i.id_ref) for i in rp_pathway.getListOfMembers()], key=lambda tup: tup[0], reverse=True)[0][1]
        #for reaction_id in [i.getId() for i in self.model.getListOfReactions()]:
        for species_id in set([i.getSpecies() for i in model.getReaction(reaction_id).getListOfReactants()]+[i.getSpecies() for i in model.getReaction(reaction_id).getListOfProducts()]):
            if rpsbml==None:
                isSpePro = self.isSpeciesProduct(species_id, [reaction_id])
            else:
                isSpePro = rpsbml.isSpeciesProduct(species_id, [reaction_id])
            if not isSpePro:
                #create the step
                createStep = {'rule_id': None,
                              'left': {species_id.split('__')[0]: 1},
                              'right': {},
                              'step': None,
                              'sub_step': None,
                              'path_id': None,
                              'transformation_id': None,
                              'rule_score': None,
                              'rule_ori_reac': None}
                #create the model in the
                if rpsbml==None:
                    self.createReaction('create_'+species_id,
                                        upper_flux_bound,
                                        lower_flux_bound,
                                        createStep,
                                        compartment_id)
                else:
                    rpsbml.createReaction('create_'+species_id,
                                        upper_flux_bound,
                                        lower_flux_bound,
                                        createStep,
                                        compartment_id)


    #########################################################################
    ############################# MODEL CREATION FUNCTIONS ##################
    #########################################################################


    ## Create libSBML model instance
    #
    # Function that creates a new libSBML model instance and initiates it with the appropriate packages. Creates a cytosol compartment
    #
    # @param name The name of the model
    # @param model_id The id of the mode
    # @param meta_id meta_id of the model. Default None means that we will generate a hash from the model_id
    def createModel(self, name, model_id, meta_id=None):
        ## sbmldoc
        self.sbmlns = libsbml.SBMLNamespaces(3,1)
        rpSBML._checklibSBML(self.sbmlns, 'generating model namespace')
        rpSBML._checklibSBML(self.sbmlns.addPkgNamespace('groups',1), 'Add groups package')
        rpSBML._checklibSBML(self.sbmlns.addPkgNamespace('fbc',2), 'Add FBC package')
        #sbmlns = libsbml.SBMLNamespaces(3,1,'groups',1)
        self.document = libsbml.SBMLDocument(self.sbmlns)
        rpSBML._checklibSBML(self.document, 'generating model doc')
        #!!!! must be set to false for no apparent reason
        rpSBML._checklibSBML(self.document.setPackageRequired('fbc', False), 'enabling FBC package')
        #!!!! must be set to false for no apparent reason
        rpSBML._checklibSBML(self.document.setPackageRequired('groups', False), 'enabling groups package')
        ## sbml model
        self.model = self.document.createModel()
        rpSBML._checklibSBML(self.model, 'generating the model')
        rpSBML._checklibSBML(self.model.setId(model_id), 'setting the model ID')
        model_fbc = self.model.getPlugin('fbc')
        model_fbc.setStrict(True)
        if meta_id==None:
            meta_id = self._genMetaID(model_id)
        rpSBML._checklibSBML(self.model.setMetaId(meta_id), 'setting model meta_id')
        rpSBML._checklibSBML(self.model.setName(name), 'setting model name')
        rpSBML._checklibSBML(self.model.setTimeUnits('second'), 'setting model time unit')
        rpSBML._checklibSBML(self.model.setExtentUnits('mole'), 'setting model compartment unit')
        rpSBML._checklibSBML(self.model.setSubstanceUnits('mole'), 'setting model substance unit')


    ## Create libSBML compartment
    #
    # cytoplasm compartment TODO: consider seperating it in another function if another compartment is to be created
    #
    # @param model libSBML model object to add the compartment
    # @param size Set the compartement size
    # @return boolean Execution success
    #TODO: set the compName as None by default. To do that you need to regenerate the compXref to
    #use MNX ids as keys instead of the string names
    def createCompartment(self, size, compId, compName, compXref, meta_id=None):
        comp = self.model.createCompartment()
        rpSBML._checklibSBML(comp, 'create compartment')
        rpSBML._checklibSBML(comp.setId(compId), 'set compartment id')
        if compName:
            rpSBML._checklibSBML(comp.setName(compName), 'set the name for the cytoplam')
        rpSBML._checklibSBML(comp.setConstant(True), 'set compartment "constant"')
        rpSBML._checklibSBML(comp.setSize(size), 'set compartment "size"')
        rpSBML._checklibSBML(comp.setSBOTerm(290), 'set SBO term for the cytoplasm compartment')
        if meta_id==None:
            meta_id = self._genMetaID(compId)
        rpSBML._checklibSBML(comp.setMetaId(meta_id), 'set the meta_id for the compartment')
        ############################ MIRIAM ############################
        comp.setAnnotation(libsbml.XMLNode.convertStringToXMLNode(self._defaultMIRIAMAnnot(meta_id)))
        # print(libsbml.XMLNode.convertXMLNodeToString(comp.getAnnotation()))
        self.addUpdateMIRIAM(comp, 'compartment', compXref, meta_id)
        # print(libsbml.XMLNode.convertXMLNodeToString(comp.getAnnotation()))
        # print()


    ## Create libSBML unit definition
    #
    # Function that creates a unit definition (composed of one or more units)
    #
    # @param model libSBML model to add the unit definition
    # @param unit_id ID for the unit definition
    # @param meta_id meta_id for the unit definition. If None creates a hash from unit_id
    # @return Unit definition
    def createUnitDefinition(self, unit_id, meta_id=None):
        unitDef = self.model.createUnitDefinition()
        rpSBML._checklibSBML(unitDef, 'creating unit definition')
        rpSBML._checklibSBML(unitDef.setId(unit_id), 'setting id')
        if meta_id==None:
            meta_id = self._genMetaID(unit_id)
        rpSBML._checklibSBML(unitDef.setMetaId(meta_id), 'setting meta_id')
        #self.unitDefinitions.append(unit_id)
        return unitDef


    ## Create libSBML unit
    #
    # Function that created a unit
    #
    # @param unitDef libSBML unit definition
    # @param libsmlunit libSBML unit parameter
    # @param exponent Value for the exponent (ex 10^5 mol/sec)
    # @param scale Value for the scale
    # @param multiplier Value for the multiplie
    # @return Unit
    def createUnit(self, unitDef, libsbmlunit, exponent, scale, multiplier):
        unit = unitDef.createUnit()
        rpSBML._checklibSBML(unit, 'creating unit')
        rpSBML._checklibSBML(unit.setKind(libsbmlunit), 'setting the kind of unit')
        rpSBML._checklibSBML(unit.setExponent(exponent), 'setting the exponenent of the unit')
        rpSBML._checklibSBML(unit.setScale(scale), 'setting the scale of the unit')
        rpSBML._checklibSBML(unit.setMultiplier(multiplier), 'setting the multiplier of the unit')


    ## Create libSBML parameters
    #
    # Parameters, in our case, are used for the bounds for FBA analysis. Unit parameter must be an instance of unitDefinition
    #
    # @param parameter_id SBML id
    # @param value Float value for this parameter
    # @param unit libSBML unit parameter
    # @param meta_id String Optional parameter for SBML meta_id
    # @return libSBML parameter object
    def createReturnFluxParameter(self,
            value,
            unit='mmol_per_gDW_per_hr',
            is_constant=True,
            parameter_id=None,
            meta_id=None):
        if parameter_id:
            param_id = parameter_id
        else:
            if value>=0:
                param_id = 'B_'+str(round(abs(value), 4)).replace('.', '_')
            else:
                param_id = 'B__'+str(round(abs(value), 4)).replace('.', '_')
        if param_id in [i.getId() for i in self.model.getListOfParameters()]:
            return self.model.getParameter(param_id)
        else:
            newParam = self.model.createParameter()
            rpSBML._checklibSBML(newParam, 'Creating a new parameter object')
            rpSBML._checklibSBML(newParam.setConstant(is_constant), 'setting as constant')
            rpSBML._checklibSBML(newParam.setId(param_id), 'setting ID')
            rpSBML._checklibSBML(newParam.setValue(value), 'setting value')
            rpSBML._checklibSBML(newParam.setUnits(unit), 'setting units')
            rpSBML._checklibSBML(newParam.setSBOTerm(625), 'setting SBO term')
            if meta_id==None:
                meta_id = self._genMetaID(parameter_id)
            rpSBML._checklibSBML(newParam.setMetaId(meta_id), 'setting meta ID')
            #self.parameters.append(parameter_id)
            return newParam


    ## Create libSBML reaction
    #
    # Create a reaction. fluxBounds is a list of libSBML.UnitDefinition, length of exactly 2 with the first position that is the upper bound and the second is the lower bound. reactants_dict and reactants_dict are dictionnaries that hold the following parameters: name, compartment, stoichiometry
    #
    # @param name Name for the reaction
    # @param reaction_id Reaction ID
    # @param fluxUpperBounds FBC id for the upper flux bound for this reaction
    # @param fluxLowerBounds FBC id for the lower flux bound for this reaction
    # @param step 2D dictionnary with the following structure {'left': {'name': stoichiometry, ...}, 'right': {}}
    # @param reaction_smiles String smiles description of this reaction (added in BRSYNTH annotation)
    # @param compartment_id String Optinal parameter compartment ID
    # @param isTarget Boolean Flag to suppress the warning that the passed step is missing information. Used in this case for the target compound
    # @param hetero_group Groups Optional parameter object that holds all the heterologous pathways
    # @param meta_id String Optional parameter reaction meta_id
    # @return meta_id meta ID for this reaction
    #TODO as of now not generic, works when creating a new SBML file, but no checks if modifying existing SBML file
    def createReaction(self,
                       reac_id,
                       fluxUpperBound,
                       fluxLowerBound,
                       step,
                       compartment_id,
                       reaction_smiles=None,
                       reacXref={},
                       pathway_id=None,
                       meta_id=None):
        reac = self.model.createReaction()
        rpSBML._checklibSBML(reac, 'create reaction')
        ################ FBC ####################
        reac_fbc = reac.getPlugin('fbc')
        rpSBML._checklibSBML(reac_fbc, 'extending reaction for FBC')
        #bounds
        upper_bound = self.createReturnFluxParameter(fluxUpperBound)
        lower_bound = self.createReturnFluxParameter(fluxLowerBound)
        rpSBML._checklibSBML(reac_fbc.setUpperFluxBound(upper_bound.getId()), 'setting '+str(reac_id)+' upper flux bound')
        rpSBML._checklibSBML(reac_fbc.setLowerFluxBound(lower_bound.getId()), 'setting '+str(reac_id)+' lower flux bound')
        #########################################
        #reactions
        rpSBML._checklibSBML(reac.setId(reac_id), 'set reaction id') #same convention as cobrapy
        rpSBML._checklibSBML(reac.setSBOTerm(176), 'setting the system biology ontology (SBO)') #set as process
        #TODO: consider having the two parameters as input to the function
        rpSBML._checklibSBML(reac.setReversible(True), 'set reaction reversibility flag')
        rpSBML._checklibSBML(reac.setFast(False), 'set reaction "fast" attribute')
        if meta_id==None:
            meta_id = self._genMetaID(reac_id)
        rpSBML._checklibSBML(reac.setMetaId(meta_id), 'setting species meta_id')
        #TODO: check that the species exist
        #reactants_dict
        for reactant in step['left']:
            spe = reac.createReactant()
            rpSBML._checklibSBML(spe, 'create reactant')
            #use the same writing convention as CobraPy
            rpSBML._checklibSBML(spe.setSpecies(str(reactant)+'__64__'+str(compartment_id)), 'assign reactant species')
            #TODO: check to see the consequences of heterologous parameters not being constant
            rpSBML._checklibSBML(spe.setConstant(True), 'set "constant" on species '+str(reactant))
            rpSBML._checklibSBML(spe.setStoichiometry(float(step['left'][reactant])),
                'set stoichiometry ('+str(float(step['left'][reactant]))+')')
        #TODO: check that the species exist
        #products_dict
        for product in step['right']:
            pro = reac.createProduct()
            rpSBML._checklibSBML(pro, 'create product')
            rpSBML._checklibSBML(pro.setSpecies(str(product)+'__64__'+str(compartment_id)), 'assign product species')
            #TODO: check to see the consequences of heterologous parameters not being constant
            rpSBML._checklibSBML(pro.setConstant(True), 'set "constant" on species '+str(product))
            rpSBML._checklibSBML(pro.setStoichiometry(float(step['right'][product])),
                'set the stoichiometry ('+str(float(step['right'][product]))+')')
        ############################ MIRIAM ############################
        rpSBML._checklibSBML(reac.setAnnotation(self._defaultBothAnnot(meta_id)), 'creating annotation')
        self.addUpdateMIRIAM(reac, 'reaction', reacXref, meta_id)
        ###### BRSYNTH additional information ########
        if reaction_smiles:
            self.addUpdateBRSynth(reac, 'smiles', reaction_smiles, None, True, False, False, meta_id)
        if step['rule_id']:
            self.addUpdateBRSynth(reac, 'rule_id', step['rule_id'], None, True, False, False, meta_id)
        #TODO: need to change the name and content (to dict) upstream
        if step['rule_ori_reac']:
            self.addUpdateBRSynth(reac, 'rule_ori_reac', step['rule_ori_reac'], None, True, False, False, meta_id)
            #self.addUpdateBRSynthList(reac, 'rule_ori_reac', step['rule_ori_reac'], True, False, meta_id)
            #sbase_obj, annot_header, value, units=None, isAlone=False, isList=False, isSort=True, meta_id=None)
        if step['rule_score']:
            self.rules_scores = (self.rules_scores[0]+step['rule_score'], self.rules_scores[1]+1)
            self.addUpdateBRSynth(reac, 'rule_score', step['rule_score'], None, False, False, False, meta_id)
        if step['path_id']:
            self.addUpdateBRSynth(reac, 'path_id', step['path_id'], None, False, False, False, meta_id)
        if step['step']:
            self.addUpdateBRSynth(reac, 'step_id', step['step'], None, False, False, False, meta_id)
        if step['sub_step']:
            self.addUpdateBRSynth(reac, 'sub_step_id', step['sub_step'], None, False, False, False, meta_id)
        #### GROUPS #####
        if not pathway_id==None:
            groups_plugin = self.model.getPlugin('groups')
            hetero_group = groups_plugin.getGroup(pathway_id)
            if not hetero_group:
                logging.warning('The pathway_id '+str(pathway_id)+' does not exist in the model')
            else:
                newM = hetero_group.createMember()
                rpSBML._checklibSBML(newM, 'Creating a new groups member')
                rpSBML._checklibSBML(newM.setIdRef(reac_id), 'Setting name to the groups member')


    ## Create libSBML reaction
    #
    # Create a reaction. fluxBounds is a list of libSBML.UnitDefinition, length of exactly 2 with the first position that is the upper bound and the second is the lower bound. reactants_dict and reactants_dict are dictionnaries that hold the following parameters: name, compartment_id, stoichiometry
    #
    # @param chemIdDictionnary containing all the cross references that we know of, can be empty)
    # @param chemXref Dictionnary containing all the cross references that we know of, can be empty
    # @param meta_id Name for the reaction
    # @param inchi String Inchi associated with this species
    # @param smiles String SMILES associated with this species
    # @param compartment_id String Set this species to belong to another compartment_id than the one globally set by self.compartment_id
    # @param charge Optional parameter describing the charge of the molecule of interest
    # @param chemForm Optional chemical formulae of the substrate (not SMILES or InChI)
    # @param dG Optinal Thermodynamics constant for this species
    # @param dG_uncert Optional Uncertainty associated with the thermodynamics of the reaction
    def createSpecies(self,
                      species_id,
                      compartment_id,
                      species_name=None,
                      chemXref={},
                      inchi=None,
                      inchikey=None,
                      smiles=None,
                      species_group_id=None,
                      in_sink_group_id=None,
                      meta_id=None):
                      #TODO: add these at some point -- not very important
                      #charge=0,
                      #chemForm=''):
        spe = self.model.createSpecies()
        rpSBML._checklibSBML(spe, 'create species')
        ##### FBC #####
        spe_fbc = spe.getPlugin('fbc')
        rpSBML._checklibSBML(spe_fbc, 'creating this species as an instance of FBC')
        #spe_fbc.setCharge(charge) #### These are not required for FBA
        #spe_fbc.setChemicalFormula(chemForm) #### These are not required for FBA
        #if compartment_id:
        rpSBML._checklibSBML(spe.setCompartment(compartment_id), 'set species spe compartment')
        #else:
        #    #removing this could lead to errors with xref
        #    rpSBML._checklibSBML(spe.setCompartment(self.compartment_id), 'set species spe compartment')
        #ID same structure as cobrapy
        #TODO: determine if this is always the case or it will change
        rpSBML._checklibSBML(spe.setHasOnlySubstanceUnits(False), 'set substance units')
        rpSBML._checklibSBML(spe.setBoundaryCondition(False), 'set boundary conditions')
        rpSBML._checklibSBML(spe.setConstant(False), 'set constant')
        #useless for FBA (usefull for ODE) but makes Copasi stop complaining
        rpSBML._checklibSBML(spe.setInitialConcentration(1.0), 'set an initial concentration')
        #same writting convention as COBRApy
        rpSBML._checklibSBML(spe.setId(str(species_id)+'__64__'+str(compartment_id)), 'set species id')
        if meta_id==None:
            meta_id = self._genMetaID(species_id)
        rpSBML._checklibSBML(spe.setMetaId(meta_id), 'setting reaction meta_id')
        if species_name==None:
            rpSBML._checklibSBML(spe.setName(species_id), 'setting name for the metabolite '+str(species_id))
        else:
            rpSBML._checklibSBML(spe.setName(species_name), 'setting name for the metabolite '+str(species_name))
        #this is setting MNX id as the name
        #this is setting the name as the input name
        #rpSBML._checklibSBML(spe.setAnnotation(self._defaultBRSynthAnnot(meta_id)), 'creating annotation')
        rpSBML._checklibSBML(spe.setAnnotation(self._defaultBothAnnot(meta_id)), 'creating annotation')
        ###### annotation ###
        self.addUpdateMIRIAM(spe, 'species', chemXref, meta_id)
        ###### BRSYNTH additional information ########
        if smiles:
            self.addUpdateBRSynth(spe, 'smiles', smiles, None, True, False, False, meta_id)
            #                   sbase_obj, annot_header, value, units=None, isAlone=False, isList=False, isSort=True, meta_id=None)
        if inchi:
            self.addUpdateBRSynth(spe, 'inchi', inchi, None, True, False, False, meta_id)
        if inchikey:
            self.addUpdateBRSynth(spe, 'inchikey', inchikey, None, True, False, False, meta_id)
        #### GROUPS #####
        #TODO: check that it actually exists
        if not species_group_id==None:
            groups_plugin = self.model.getPlugin('groups')
            hetero_group = groups_plugin.getGroup(species_group_id)
            if not hetero_group:
                logging.warning('The species_group_id '+str(species_group_id)+' does not exist in the model')
                #TODO: consider creating it if
            else:
                newM = hetero_group.createMember()
                rpSBML._checklibSBML(newM, 'Creating a new groups member')
                rpSBML._checklibSBML(newM.setIdRef(str(species_id)+'__64__'+str(compartment_id)), 'Setting name to the groups member')
        #TODO: check that it actually exists
        #add the species to the sink species
        logging.debug('in_sink_group_id: '+str(in_sink_group_id))
        if not in_sink_group_id==None:
            groups_plugin = self.model.getPlugin('groups')
            sink_group = groups_plugin.getGroup(in_sink_group_id)
            if not sink_group:
                logging.warning('The species_group_id '+str(in_sink_group_id)+' does not exist in the model')
                #TODO: consider creating it if
            else:
                newM = sink_group.createMember()
                rpSBML._checklibSBML(newM, 'Creating a new groups member')
                rpSBML._checklibSBML(newM.setIdRef(str(species_id)+'__64__'+str(compartment_id)), 'Setting name to the groups member')


    ## Create libSBML pathway
    #
    # Create the collection of reactions that constitute the pathway using the Groups package and create the custom IBIBSA annotations
    #
    # @param model libSBML model to add the unit definition
    # @param reaction_id Reaction ID
    # @param name Name for the reaction
    # @param fluxBounds list of size 2 that describe the FBC upper and lower bounds for this reactions flux
    # @param reactants list of species that are the reactants of this reaction
    # @param products list of species that are the products of this reaction
    # @param reaction_smiles String smiles description of this reaction (added in BRSYNTH annotation)
    # @return hetero_group The number libSBML groups object to pass to createReaction to categorise the new reactions
    def createPathway(self, pathway_id, meta_id=None):
        groups_plugin = self.model.getPlugin('groups')
        new_group = groups_plugin.createGroup()
        new_group.setId(pathway_id)
        if meta_id==None:
            meta_id = self._genMetaID(pathway_id)
        new_group.setMetaId(meta_id)
        new_group.setKind(libsbml.GROUP_KIND_COLLECTION)
        new_group.setAnnotation(self._defaultBRSynthAnnot(meta_id))


    ## Create libSBML gene
    #
    # Create the list of genes in the model including its custom BRSYNTH annotatons
    #
    # @param model libSBML model to add the unit definition
    # @param reac libSBML reaction object
    # @param step_id The step for the number of
    # @return libSBML gene object
    def createGene(self, reac, step_id, meta_id=None):
        #TODO: pass this function to Pablo for him to fill with parameters that are appropriate for his needs
        geneName = 'RP'+str(step_id)+'_gene'
        fbc_plugin = self.model.getPlugin('fbc')
        #fbc_plugin = reac.getPlugin("fbc")
        gp = fbc_plugin.createGeneProduct()
        gp.setId(geneName)
        if meta_id==None:
            meta_id = self._genMetaID(str(geneName))
        gp.setMetaId(meta_id)
        gp.setLabel('gene_'+str(step_id))
        gp.setAssociatedSpecies('RP'+str(step_id))
        ##### NOTE: The parameters here require the input from Pablo to determine what he needs
        #gp.setAnnotation(self._defaultBothAnnot(meta_id))


    ## Create libSBML flux objective
    # WARNING DEPRECATED -- use the createMultiFluxObj() with lists of size one to define an objective function
    # with a single reaction
    # Using the FBC package one can add the FBA flux objective directly to the model. This function sets a particular reaction as objective with maximization or minimization objectives
    #
    # @param model libSBML model to add the unit definition
    # @param fluxobj_id The id given to this particular objective
    # @param reactionName The name or id of the reaction that we are setting a flux objective
    # @param coefficient FBA coefficient
    # @param isMax Boolean to determine if we are maximizing or minimizing the objective
    # @param meta_id Set the meta_id
    # @return Boolean exit code
    def createFluxObj(self, fluxobj_id, reactionName, coefficient, isMax=True, meta_id=None):
        fbc_plugin = self.model.getPlugin('fbc')
        target_obj = fbc_plugin.createObjective()
        #TODO: need to define inpiut metaID
        target_obj.setAnnotation(self._defaultBRSynthAnnot(meta_id))
        target_obj.setId(fluxobj_id)
        if isMax:
            target_obj.setType('maximize')
        else:
            target_obj.setType('minimize')
        fbc_plugin.setActiveObjectiveId(fluxobj_id) # this ensures that we are using this objective when multiple
        target_flux_obj = target_obj.createFluxObjective()
        target_flux_obj.setReaction(reactionName)
        target_flux_obj.setCoefficient(coefficient)
        if meta_id==None:
            meta_id = self._genMetaID(str(fluxobj_id))
        target_flux_obj.setMetaId(meta_id)
        target_flux_obj.setAnnotation(self._defaultBRSynthAnnot(meta_id))


    ## Create libSBML flux objective
    #
    # Using the FBC package one can add the FBA flux objective directly to the model. This function sets a particular reaction as objective with maximization or minimization objectives
    #
    # @param model libSBML model to add the unit definition
    # @param fluxobj_id The id given to this particular objective
    # @param reactionName The name or id of the reaction that we are setting a flux objective
    # @param coefficient FBA coefficient
    # @param isMax Boolean to determine if we are maximizing or minimizing the objective
    # @param meta_id Set the meta_id
    # @return Boolean exit code
    def createMultiFluxObj(self, fluxobj_id, reactionNames, coefficients, isMax=True, meta_id=None):
        if not len(reactionNames)==len(coefficients):
            logging.error('The size of reactionNames is not the same as coefficients')
            return False
        fbc_plugin = self.model.getPlugin('fbc')
        target_obj = fbc_plugin.createObjective()
        target_obj.setAnnotation(self._defaultBRSynthAnnot(meta_id))
        target_obj.setId(fluxobj_id)
        if isMax:
            target_obj.setType('maximize')
        else:
            target_obj.setType('minimize')
        fbc_plugin.setActiveObjectiveId(fluxobj_id) # this ensures that we are using this objective when multiple
        for reac, coef in zip(reactionNames, coefficients):
            target_flux_obj = target_obj.createFluxObjective()
            target_flux_obj.setReaction(reac)
            target_flux_obj.setCoefficient(coef)
            if meta_id==None:
                meta_id = self._genMetaID(str(fluxobj_id))
            target_flux_obj.setMetaId(meta_id)
            target_flux_obj.setAnnotation(self._defaultBRSynthAnnot(meta_id))


    ##############################################################################################
    ############################### Generic Model ################################################
    ##############################################################################################


    ## Generate a generic model
    #
    # Since we will be using the same type of parameters for the RetroPath model, this function
    # generates a libSBML model with parameters that will be mostly used
    #
    #
    #
    def genericModel(self,
                     modelName,
                     model_id,
                     compXref,
                     compartment_id,
                     upper_flux_bound=999999,
                     lower_flux_bound=0):
        self.createModel(modelName, model_id)
        # mmol_per_gDW_per_hr -- flux
        unitDef = self.createUnitDefinition('mmol_per_gDW_per_hr')
        self.createUnit(unitDef, libsbml.UNIT_KIND_MOLE, 1, -3, 1)
        self.createUnit(unitDef, libsbml.UNIT_KIND_GRAM, 1, 0, 1)
        self.createUnit(unitDef, libsbml.UNIT_KIND_SECOND, 1, 0, 3600)
        # kj_per_mol -- thermodynamics
        gibbsDef = self.createUnitDefinition('kj_per_mol')
        self.createUnit(gibbsDef, libsbml.UNIT_KIND_JOULE, 1, 3, 1)
        self.createUnit(gibbsDef, libsbml.UNIT_KIND_MOLE, -1, 1, 1)
        ### set the bounds
        upBound = self.createReturnFluxParameter(upper_flux_bound)
        lowBound = self.createReturnFluxParameter(lower_flux_bound)
        #compartment
        #TODO: create a new compartment
        #self.createCompartment(1, 'MNXC3', 'cytoplasm', compXref)
        #try to recover the name from the Xref
        try:
            name = compXref['name'][0]
        except KeyError:
            name = compartment_id+'_name'
        self.createCompartment(1, compartment_id, name, compXref)
