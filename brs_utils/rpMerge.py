import numpy as np
import tempfile
import logging
import pandas as pd
import rpSBML
import libsbml


##TODO: this really does not need to be an object
class rpMerge:
    def __init__(self):
        self.logger = logging.getLogger(__name__)


    #######################################################################
    ############################# PRIVATE FUNCTIONS ####################### 
    #######################################################################

    ## Check the libSBML calls
    #
    # Check that the libSBML python calls do not return error INT and if so, display the error. Taken from: http://sbml.org/Software/libSBML/docs/python-api/create_simple_model_8py-example.html
    #
    # @param value The SBML call
    # @param message The string that describes the call
    def _checklibSBML(self, value, message):
        if value is None:
            self.logger.error('LibSBML returned a null value trying to ' + message + '.')
            raise AttributeError
        elif type(value) is int:
            if value==libsbml.LIBSBML_OPERATION_SUCCESS:
                return
            else:
                err_msg = 'Error encountered trying to ' + message + '.' \
                        + 'LibSBML returned error code ' + str(value) + ': "' \
                        + libsbml.OperationReturnValue_toString(value).strip() + '"'
                self.logger.error(err_msg)
                raise AttributeError
        else:
            #self.logger.debug(message)
            return None


    ## Function to find the unique species
    #
    # pd_matrix is organised such that the rows are the simulated species and the columns are the measured ones
    #
    def _findUniqueRowColumn(self, pd_matrix):
        self.logger.debug(pd_matrix)
        to_ret = {}
        ######################## filter by the global top values ################
        self.logger.debug('################ Filter best #############')
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
                self.logger.debug('Overwriting (1): '+str(col_name))
                self.logger.debug(x)
            to_ret[col_name] = [row_name]
            #delete the rows and the columns 
            self.logger.debug('==================')
            self.logger.debug('Column: '+str(col_name))
            self.logger.debug('Row: '+str(row_name))
            pd_matrix.loc[:, col_name] = 0.0
            pd_matrix.loc[row_name, :] = 0.0
            x = pd_matrix.values
            x = np.around(x, decimals=5)
            top = np.where(x==np.max(x))
            self.logger.debug(pd_matrix)
            self.logger.debug(top)
            self.logger.debug('==================')
        #################### filter by columns (measured) top values ##############
        self.logger.debug('################ Filter by column best ############')
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
                        self.logger.warning('For col '+str(col)+' there are either better or equal values: '+str(row))
                        self.logger.warning(x)
                        continue
                    #if you perform any changes on the rows and columns, then you can perform the loop again
                    reloop = True
                    pd_entry = pd_matrix.iloc[[top_row],[col]]
                    self.logger.debug('==================')
                    row_name = pd_entry.index[0]
                    col_name = pd_entry.columns[0]
                    self.logger.debug('Column: '+str(col_name))
                    self.logger.debug('Row: '+str(row_name))
                    if col_name in to_ret:
                        self.logger.debug('Overwriting (2): '+str(col_name))
                        self.logger.debug(pd_matrix.values)
                    to_ret[col_name] = [row_name]
                    #delete the rows and the columns 
                    pd_matrix.loc[:, col_name] = 0.0
                    pd_matrix.loc[row_name, :] = 0.0
                    x = pd_matrix.values
                    x = np.around(x, decimals=5)
                    self.logger.debug(pd_matrix)
                    self.logger.debug('==================')
        ################## laslty if there are multiple values that are not 0.0 then account for that ######
        self.logger.debug('################# get the rest ##########')
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
                        self.logger.warning('At this point should never have only one: '+str(x[:,col]))
                        self.logger.warning(x)
                else:
                    for top_row in top_rows:
                        pd_entry = pd_matrix.iloc[[top_row],[col]]
                        row_name = pd_entry.index[0]
                        col_name = pd_entry.columns[0]
                        if not col_name in to_ret:
                            to_ret[col_name] = []
                        to_ret[col_name].append(row_name)
        self.logger.debug(pd_matrix)
        self.logger.debug('###################')
        return to_ret


    #######################################################################
    ###################################### INPUT FUNCTIONS ################
    #######################################################################

    def mergeSBMLFiles(self,
                       path_source, 
                       path_target,
                       path_merge,
                       species_group_id='central_species',
                       sink_species_group_id='rp_sink_species',
                       pathway_id='rp_pathway'):
        if not os.path.exists(path_source):
            self.logger.error('Source SBML file is invalid: '+str(path_source))
            return False
        if not os.path.exists(path_target):
            self.logger.error('Target SBML file is invalid: '+str(path_target))
            return False
        source_rpsbml = rpSBML.rpSBML('source', path=path_source)
        target_rpsbml = rpSBML.rpSBML('target', path=path_target)
        self.mergeModels(source_rpsbml,
                         target_rpsbml,
                         species_group_id,
                         sink_species_group_id,
                         pathway_id)
        target_rpsbml.writeSBML(path_merge)
        return True
        


    ##########################################################################################
    #################################### REACTION ############################################
    ##########################################################################################

    ##
    # Compare that all the measured species of a reactions are found within sim species to match with a reaction.
    # We assume that there cannot be two reactions that have the same species and reactants. This is maintained by SBML
    # TODO: need to remove from the list reactions simulated reactions that have matched
    # TODO: Remove. This assumes that reactions can match multiple times, when in fact its impossible
    def compareReactions(self, species_match, target_rpsbml, source_rpsbml):
        ############## compare the reactions #######################
        #construct sim reactions with species
        self.logger.debug('------ Comparing reactions --------')
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
                self.logger.debug('\t=========== '+str(target_reaction.getId())+' ==========')
                self.logger.debug('\t+++++++ Species match +++++++')
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
                self.logger.debug('\tspecies_match: '+str(species_match))
                self.logger.debug('\tspecies_match: '+str(species_match.keys()))
                self.logger.debug('\tsim_reactants_id: '+str(sim_reactants_id))
                self.logger.debug('\tmeasured_reactants_id: '+str([i.species for i in source_reaction.getListOfReactants()]))
                self.logger.debug('\tsim_products_id: '+str(sim_products_id))
                self.logger.debug('\tmeasured_products_id: '+str([i.species for i in source_reaction.getListOfProducts()]))
                #ensure that the match is 1:1
                #1)Here we assume that a reaction cannot have twice the same species
                cannotBeSpecies = []
                #if there is a match then we loop again since removing it from the list of potential matches would be appropriate
                keep_going = True
                while keep_going:
                    self.logger.debug('\t\t----------------------------')
                    keep_going = False
                    for reactant in source_reaction.getListOfReactants():
                        self.logger.debug('\t\tReactant: '+str(reactant.species))
                        #if a species match has been found AND if such a match has been found
                        founReaIDs = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['id'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'] if not tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][i]['id']==None]
                        self.logger.debug('\t\tfounReaIDs: '+str(founReaIDs))
                        if reactant.species and reactant.species in species_match and not list(species_match[reactant.species].keys())==[] and not reactant.species in founReaIDs:
                            best_spe = [k for k, v in sorted(species_match[reactant.species].items(), key=lambda item: item[1], reverse=True)][0]
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][reactant.species] = {'id': best_spe, 'score': species_match[reactant.species][best_spe], 'found': True}
                            cannotBeSpecies.append(best_spe)
                        elif not reactant.species in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants']:
                            self.logger.warning('\t\tCould not find the following measured reactant in the matched species: '+str(reactant.species))
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][reactant.species] = {'id': None, 'score': 0.0, 'found': False}
                    for product in source_reaction.getListOfProducts():
                        self.logger.debug('\t\tProduct: '+str(product.species))
                        foundProIDs = [tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['id'] for i in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'] if not tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][i]['id']==None]
                        self.logger.debug('\t\tfoundProIDs: '+str(foundProIDs))
                        if product.species and product.species in species_match and not list(species_match[product.species].keys())==[] and not product.species in foundProIDs:
                            best_spe = [k for k, v in sorted(species_match[product.species].items(), key=lambda item: item[1], reverse=True)][0]
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['reactants'][product.species] = {'id': best_spe, 'score': species_match[product.species][best_spe], 'found': True}
                            cannotBeSpecies.append(best_spe)
                        elif not product.species in tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products']:
                            self.logger.warning('\t\tCould not find the following measured product in the matched species: '+str(product.species))
                            tmp_reaction_match[source_reaction.getId()][target_reaction.getId()]['products'][product.species] = {'id': None, 'score': 0.0, 'found': False}
                    self.logger.debug('\t\tcannotBeSpecies: '+str(cannotBeSpecies))
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
        unique = self._findUniqueRowColumn(pd.DataFrame(source_target))
        self.logger.debug('findUniqueRowColumn')
        self.logger.debug(unique)
        reaction_match = {}
        for meas in source_target:
            reaction_match[meas] = {'id': None, 'score': 0.0, 'found': False}
            if meas in unique:
                if len(unique[meas])>1:
                    self.logger.debug('Multiple values may match, choosing the first arbitrarily: '+str(unique))
                reaction_match[meas]['id'] = unique[meas]
                reaction_match[meas]['score'] = round(tmp_reaction_match[meas][unique[meas][0]]['score'], 5)
                reaction_match[meas]['found'] = tmp_reaction_match[meas][unique[meas][0]]['found']
        #### compile a reaction score based on the ec and species scores
        self.logger.debug(tmp_reaction_match)
        self.logger.debug(reaction_match)
        self.logger.debug('-------------------------------')
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
                self.logger.debug('Cannot find the source species '+str(source_reactant.species)+' in the target species: '+str(species_source_target))
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
                self.logger.debug('Cannot find the measured species '+str(source_product.species)+' in the the matched species: '+str(species_source_target))
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
    def compareReaction(self, species_source_target, source_reaction, target_reaction):
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
        self.logger.debug('source_reactants: '+str(source_reactants))
        self.logger.debug('target_reactants: '+str(target_reactants))
        self.logger.debug('source_products: '+str(source_products))
        self.logger.debug('target_products: '+str(target_products))
        self.logger.debug(set(source_reactants)-set(target_reactants))
        self.logger.debug(set(source_products)-set(target_products))
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
    def compareSpecies(self, comp_source_target, source_rpsbml, target_rpsbml):
        ############## compare species ###################
        source_target = {}
        target_source = {}
        species_match = {}
        for source_species in source_rpsbml.model.getListOfSpecies():
            self.logger.debug('--- Trying to match chemical species: '+str(source_species.getId())+' ---')
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
                    self.logger.debug('--> Matched MIRIAM: '+str(target_species.getId()))
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
                        self.logger.warning('There are multiple inchikey values, taking the first one: '+str(source_miriam_annot['inchikey']))
                    source_inchikey_split = source_miriam_annot['inchikey'][0].split('-')
                if 'inchikey' in target_brsynth_annot:
                    target_inchikey_split = target_brsynth_annot['inchikey'].split('-')
                elif 'inchikey' in target_miriam_annot:
                    if not len(target_miriam_annot['inchikey'])==1:
                        #TODO: handle mutliple inchikey with mutliple compare and the highest comparison value kept
                        self.logger.warning('There are multiple inchikey values, taking the first one: '+str(target_brsynth_annot['inchikey']))
                    target_inchikey_split = target_miriam_annot['inchikey'][0].split('-')
                if source_inchikey_split and target_inchikey_split:
                    if source_inchikey_split[0]==target_inchikey_split[0]:
                        self.logger.debug('Matched first layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
                        source_target[source_species.getId()][target_species.getId()]['score'] += 0.2
                        if source_inchikey_split[1]==target_inchikey_split[1]:
                            self.logger.debug('Matched second layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
                            source_target[source_species.getId()][target_species.getId()]['score'] += 0.2
                            source_target[source_species.getId()][target_species.getId()]['found'] = True
                            if source_inchikey_split[2]==target_inchikey_split[2]:
                                self.logger.debug('Matched third layer InChIkey: ('+str(source_inchikey_split)+' -- '+str(target_inchikey_split)+')')
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
        unique = self._findUniqueRowColumn(pd.DataFrame(source_target_mat))
        self.logger.debug('findUniqueRowColumn:')
        self.logger.debug(unique)
        for meas in source_target:
            if meas in unique:
                species_match[meas] = {}
                for unique_spe in unique[meas]:
                    species_match[meas][unique_spe] = round(source_target[meas][unique[meas][0]]['score'], 5)
            else:
                self.logger.warning('Cannot find a species match for the measured species: '+str(meas))
        self.logger.debug('#########################')
        self.logger.debug('species_match:')
        self.logger.debug(species_match)
        self.logger.debug('-----------------------')
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
            self.logger.debug('Measured: ')
            self.logger.debug(measured_frac_ec)
            self.logger.debug('Simulated: ')
            self.logger.debug(sim_frac_ec)
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
            self.logger.warning('One of the two reactions does not have any EC entries.\nMeasured: '+str(meas_reac_miriam)+' \nSimulated: '+str(sim_reac_miriam))
            return 0.0



    #############################################################################################################
    ############################################ MERGE ##########################################################
    #############################################################################################################


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
    def mergeModels(self,
                    source_rpsbml,
                    target_rpsbml,
                    species_group_id='central_species',
                    sink_species_group_id='rp_sink_species',
                    pathway_id='rp_pathway'):
        #target_rpsbml.model = target_document.getModel()
        #Find the ID's of the similar target_rpsbml.model species
        ################ MODEL FBC ########################
        if not target_rpsbml.model.isPackageEnabled('fbc'):
            self._checklibSBML(target_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/fbc/version2',
                'fbc',
                True),
                    'Enabling the FBC package')
        if not source_rpsbml.model.isPackageEnabled('fbc'):
            self._checklibSBML(source_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/fbc/version2',
                'fbc',
                True),
                    'Enabling the FBC package')
        target_fbc = target_rpsbml.model.getPlugin('fbc')
        source_fbc = source_rpsbml.model.getPlugin('fbc')
        #note sure why one needs to set this as False
        self._checklibSBML(source_rpsbml.document.setPackageRequired('fbc', False), 'enabling FBC package')
        ################ UNITDEFINITIONS ######
        #return the list of unit definitions id's for the target to avoid overwritting
        #WARNING: this means that the original unit definitions will be prefered over the new one
        target_unitDefID = [i.getId() for i in target_rpsbml.model.getListOfUnitDefinitions()]
        for source_unitDef in source_rpsbml.model.getListOfUnitDefinitions():
            if not source_unitDef.getId() in target_unitDefID: #have to compare by ID since no annotation
                #create a new unitDef in the target
                target_unitDef = target_rpsbml.model.createUnitDefinition()
                self._checklibSBML(target_unitDef, 'fetching target unit definition')
                #copy unitDef info to the target
                self._checklibSBML(target_unitDef.setId(source_unitDef.getId()),
                    'setting target unit definition ID')
                self._checklibSBML(target_unitDef.setAnnotation(source_unitDef.getAnnotation()),
                    'setting target unit definition Annotation')
                for source_unit in source_unitDef.getListOfUnits():
                    #copy unit info to the target unitDef
                    target_unit = target_unitDef.createUnit()
                    self._checklibSBML(target_unit, 'creating target unit')
                    self._checklibSBML(target_unit.setKind(source_unit.getKind()),
                        'setting target unit kind')
                    self._checklibSBML(target_unit.setExponent(source_unit.getExponent()),
                        'setting target unit exponent')
                    self._checklibSBML(target_unit.setScale(source_unit.getScale()),
                        'setting target unit scale')
                    self._checklibSBML(target_unit.setMultiplier(source_unit.getMultiplier()),
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
                self.logger.warning('No annotation for the source of compartment '+str(source_compartment.getId()))
                continue
            #compare by MIRIAM first
            for target_compartment in target_rpsbml.model.getListOfCompartments():
                target_annotation = target_compartment.getAnnotation()
                if not target_annotation:
                    self.logger.warning('No annotation for the target of compartment: '+str(target_compartment.getId()))
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
                    self._checklibSBML(target_compartment, 'Creating target compartment')
                    self._checklibSBML(target_compartment.setMetaId(source_compartment.getMetaId()),
                            'setting target metaId')
                    #make sure that the ID is different
                    if source_compartment.getId()==target_compartment.getId():
                        self._checklibSBML(target_compartment.setId(source_compartment.getId()+'_sourceModel'),
                                'setting target id')
                    else:
                        self._checklibSBML(target_compartment.setId(source_compartment.getId()),
                                'setting target id')
                    self._checklibSBML(target_compartment.setName(source_compartment.getName()),
                            'setting target name')
                    self._checklibSBML(target_compartment.setConstant(source_compartment.getConstant()),
                            'setting target constant')
                    self._checklibSBML(target_compartment.setAnnotation(source_compartment.getAnnotation()),
                            'setting target annotation')
                    self._checklibSBML(target_compartment.setSBOTerm(source_compartment.getSBOTerm()),
                            'setting target annotation')
                    comp_source_target[target_compartment.getId()] = target_compartment.getId() 
        self.logger.debug('comp_source_target: '+str(comp_source_target))
        ################ PARAMETERS ###########
        #WARNING: here we compare by ID
        targetParametersID = [i.getId() for i in target_rpsbml.model.getListOfParameters()]
        for source_parameter in source_rpsbml.model.getListOfParameters():
            if not source_parameter.getId() in targetParametersID:
                target_parameter = target_rpsbml.model.createParameter()
                self._checklibSBML(target_parameter, 'creating target parameter')
                self._checklibSBML(target_parameter.setId(source_parameter.getId()), 'setting target parameter ID')
                self._checklibSBML(target_parameter.setSBOTerm(source_parameter.getSBOTerm()),
                    'setting target parameter SBO')
                self._checklibSBML(target_parameter.setUnits(source_parameter.getUnits()),
                    'setting target parameter Units')
                self._checklibSBML(target_parameter.setValue(source_parameter.getValue()),
                    'setting target parameter Value')
                self._checklibSBML(target_parameter.setConstant(source_parameter.getConstant()),
                    'setting target parameter ID')
        ################ FBC GENE PRODUCTS ########################
        #WARNING: here we compare by ID
        targetGenProductID = [i.getId() for i in target_fbc.getListOfGeneProducts()]
        for source_geneProduct in source_fbc.getListOfGeneProducts():
            if not source_geneProduct.getId() in targetGenProductID:
                target_geneProduct = target_fbc.createGeneProduct()
                self._checklibSBML(target_geneProduct, 'creating target gene product')
                self._checklibSBML(target_geneProduct.setId(source_geneProduct.getId()),
                    'setting target gene product id')
                self._checklibSBML(target_geneProduct.setLabel(source_geneProduct.getLabel()),
                    'setting target gene product label')
                self._checklibSBML(target_geneProduct.setName(source_geneProduct.getName()),
                    'setting target gene product name')
                self._checklibSBML(target_geneProduct.setMetaId(source_geneProduct.getMetaId()),
                    'setting target gene product meta_id')
        ############### FBC OBJECTIVES ############
        #WARNING: here we compare by ID
        targetObjectiveID = [i.getId() for i in target_fbc.getListOfObjectives()]
        sourceObjectiveID = [i.getId() for i in source_fbc.getListOfObjectives()]
        for source_objective in source_fbc.getListOfObjectives():
            if not source_objective.getId() in targetObjectiveID:
                target_objective = target_fbc.createObjective()
                self._checklibSBML(target_objective, 'creating target objective')
                self._checklibSBML(target_objective.setId(source_objective.getId()), 'setting target objective')
                self._checklibSBML(target_objective.setName(source_objective.getName()), 'setting target objective')
                self._checklibSBML(target_objective.setType(source_objective.getType()),
                        'setting target objective type')
                for source_fluxObjective in source_objective.getListOfFluxObjectives():
                    target_fluxObjective = target_objective.createFluxObjective()
                    self._checklibSBML(target_fluxObjective, 'creating target flux objective')
                    self._checklibSBML(target_fluxObjective.setName(source_fluxObjective.getName()),
                        'setting target flux objective name')
                    self._checklibSBML(target_fluxObjective.setCoefficient(source_fluxObjective.getCoefficient()),
                        'setting target flux objective coefficient')
                    self._checklibSBML(target_fluxObjective.setReaction(source_fluxObjective.getReaction()),
                        'setting target flux objective reaction')
                    self._checklibSBML(target_fluxObjective.setAnnotation(source_fluxObjective.getAnnotation()),
                        'setting target flux obj annotation from source flux obj')
                self._checklibSBML(target_objective.setAnnotation(source_objective.getAnnotation()),
                        'setting target obj annotation from source obj')
        self.logger.debug('targetObjectiveID: '+str(targetObjectiveID))
        self.logger.debug('sourceObjectiveID: '+str(sourceObjectiveID))
        ################ SPECIES ####################
        species_source_target = self.compareSpecies(comp_source_target, source_rpsbml, target_rpsbml)
        self.logger.debug('species_source_target: '+str(species_source_target))
        for source_species in species_source_target:
            list_target = [i for i in species_source_target[source_species]]
            if source_species in list_target:
                self.logger.warning('The source ('+str(source_species)+') and target species ids ('+str(list_target)+') are the same')
            #if no match then add it to the target model
            if species_source_target[source_species]=={}:
                self.logger.debug('Creating source species '+str(source_species)+' in target rpsbml')
                source_species = source_rpsbml.model.getSpecies(source_species)
                if not source_species:
                    self.logger.error('Cannot retreive model species: '+str(source_species_id))
                else:
                    self._checklibSBML(source_species, 'fetching source species')
                    targetModel_species = target_rpsbml.model.createSpecies()
                    self._checklibSBML(targetModel_species, 'creating species')
                    self._checklibSBML(targetModel_species.setMetaId(source_species.getMetaId()),
                            'setting target metaId')
                    self._checklibSBML(targetModel_species.setId(source_species.getId()),
                            'setting target id')
                    self._checklibSBML(targetModel_species.setCompartment(comp_source_target[source_species.getCompartment()]),
                            'setting target compartment')
                    self._checklibSBML(targetModel_species.setInitialConcentration(
                        source_species.getInitialConcentration()),
                            'setting target initial concentration')
                    self._checklibSBML(targetModel_species.setBoundaryCondition(
                        source_species.getBoundaryCondition()),
                            'setting target boundary concentration')
                    self._checklibSBML(targetModel_species.setHasOnlySubstanceUnits(
                        source_species.getHasOnlySubstanceUnits()),
                            'setting target has only substance units')
                    self._checklibSBML(targetModel_species.setBoundaryCondition(
                        source_species.getBoundaryCondition()),
                            'setting target boundary condition')
                    self._checklibSBML(targetModel_species.setConstant(source_species.getConstant()),
                        'setting target constant')
                    self._checklibSBML(targetModel_species.setAnnotation(source_species.getAnnotation()),
                        'setting target annotation')
        ################ REACTIONS ###################
        #TODO; consider the case where two reactions have the same ID's but are not the same reactions
        reac_replace = {}
        for source_reaction in source_rpsbml.model.getListOfReactions():
            is_found = False
            for target_reaction in target_rpsbml.model.getListOfReactions():
                score, match = self.compareReaction(species_source_target, source_reaction, target_reaction)
                if match:
                    self.logger.debug('Source reaction '+str(source_reaction)+' matches with target reaction '+str(target_reaction))
                    #source_reaction[source_reaction.getId()] = target_reaction.getId()
                    reac_replace[source_reaction.getId()] = target_reaction.getId()
                    is_found = True
                    break
            if not is_found:
                self.logger.debug('Cannot find source reaction: '+str(source_reaction.getId()))
                self._checklibSBML(source_reaction, 'fetching source reaction')
                target_reaction = target_rpsbml.model.createReaction()
                self._checklibSBML(target_reaction, 'create reaction')
                target_fbc = target_reaction.getPlugin('fbc')
                self._checklibSBML(target_fbc, 'fetching target FBC package')
                source_fbc = source_reaction.getPlugin('fbc')
                self._checklibSBML(source_fbc, 'fetching source FBC package')
                source_upperFluxBound = source_fbc.getUpperFluxBound()
                self._checklibSBML(source_upperFluxBound, 'fetching upper flux bound')
                self._checklibSBML(target_fbc.setUpperFluxBound(source_upperFluxBound),
                        'setting upper flux bound')
                source_lowerFluxBound = source_fbc.getLowerFluxBound()
                self._checklibSBML(source_lowerFluxBound, 'fetching lower flux bound')
                self._checklibSBML(target_fbc.setLowerFluxBound(source_lowerFluxBound),
                        'setting lower flux bound')
                self._checklibSBML(target_reaction.setId(source_reaction.getId()), 'set reaction id')
                self._checklibSBML(target_reaction.setName(source_reaction.getName()), 'set name')
                self._checklibSBML(target_reaction.setSBOTerm(source_reaction.getSBOTerm()),
                        'setting the reaction system biology ontology (SBO)') #set as process
                #TODO: consider having the two parameters as input to the function
                self._checklibSBML(target_reaction.setReversible(source_reaction.getReversible()),
                        'set reaction reversibility flag')
                self._checklibSBML(target_reaction.setFast(source_reaction.getFast()),
                        'set reaction "fast" attribute')
                self._checklibSBML(target_reaction.setMetaId(source_reaction.getMetaId()), 'setting species meta_id')
                self._checklibSBML(target_reaction.setAnnotation(source_reaction.getAnnotation()),
                        'setting annotation for source reaction')
                #Reactants
                self.logger.debug('Setting reactants')
                for source_reaction_reactantID in [i.species for i in source_reaction.getListOfReactants()]:
                    self.logger.debug('\tAdding '+str(source_reaction_reactantID))
                    target_reactant = target_reaction.createReactant()
                    self._checklibSBML(target_reactant, 'create target reactant')
                    if source_reaction_reactantID in species_source_target:
                        if not species_source_target[source_reaction_reactantID]=={}:
                            if len(species_source_target[source_reaction_reactantID])>1:
                                self.logger.warning('Multiple matches for '+str(source_reaction_reactantID)+': '+str(species_source_target[source_reaction_reactantID]))
                                self.logger.warning('Taking one the first one arbitrarely: '+str([i for i in species_source_target[source_reaction_reactantID]][0]))
                            #WARNING: taking the first one arbitrarely 
                            self._checklibSBML(target_reactant.setSpecies(
                                [i for i in species_source_target[source_reaction_reactantID]][0]), 'assign reactant species')
                        else:
                            self._checklibSBML(target_reactant.setSpecies(source_reaction_reactantID),
                                'assign reactant species')
                    else:
                        self._checklibSBML(target_reactant.setSpecies(source_reaction_reactantID),
                            'assign reactant species')
                    source_reactant = source_reaction.getReactant(source_reaction_reactantID)
                    self._checklibSBML(source_reactant, 'fetch source reactant')
                    self._checklibSBML(target_reactant.setConstant(source_reactant.getConstant()),
                            'set "constant" on species '+str(source_reactant.getConstant()))
                    self._checklibSBML(target_reactant.setStoichiometry(source_reactant.getStoichiometry()),
                            'set stoichiometry ('+str(source_reactant.getStoichiometry)+')')
                #Products
                self.logger.debug('Setting products')
                for source_reaction_productID in [i.species for i in source_reaction.getListOfProducts()]:
                    self.logger.debug('\tAdding '+str(source_reaction_productID))
                    target_product = target_reaction.createProduct()
                    self._checklibSBML(target_product, 'create target reactant')
                    if source_reaction_productID in species_source_target:
                        if not species_source_target[source_reaction_productID]=={}:
                            if len(species_source_target[source_reaction_reactantID])>1:
                                self.logger.warning('Multiple matches for '+str(source_reaction_productID)+': '+str(species_source_target[source_reaction_productID]))
                                self.logger.warning('Taking one arbitrarely')
                            #WARNING: taking the first one arbitrarely 
                            self._checklibSBML(target_product.setSpecies(
                                [i for i in species_source_target[source_reaction_productID]][0]), 'assign reactant product')
                        else:
                            self._checklibSBML(target_product.setSpecies(source_reaction_productID),
                                'assign reactant product')
                    else:
                        self._checklibSBML(target_product.setSpecies(source_reaction_productID),
                            'assign reactant product')
                    source_product = source_reaction.getProduct(source_reaction_productID)
                    self._checklibSBML(source_product, 'fetch source reactant')
                    self._checklibSBML(target_product.setConstant(source_product.getConstant()),
                            'set "constant" on product '+str(source_product.getConstant()))
                    self._checklibSBML(target_product.setStoichiometry(source_product.getStoichiometry()),
                            'set stoichiometry ('+str(source_product.getStoichiometry)+')')
        #### GROUPS #####
        #TODO loop through the groups to add them
        if not target_rpsbml.model.isPackageEnabled('groups'):
            self._checklibSBML(target_rpsbml.model.enablePackage(
                'http://www.sbml.org/sbml/level3/version1/groups/version1',
                'groups',
                True),
                    'Enabling the GROUPS package')
        #!!!! must be set to false for no apparent reason
        self._checklibSBML(source_rpsbml.document.setPackageRequired('groups', False), 'enabling groups package')
        source_groups = source_rpsbml.model.getPlugin('groups')
        self._checklibSBML(source_groups, 'fetching the source model groups')
        target_groups = target_rpsbml.model.getPlugin('groups')
        self._checklibSBML(target_groups, 'fetching the target model groups')
        #self.logger.debug('species_source_target: '+str(species_source_target))
        #self.logger.debug('reac_replace: '+str(reac_replace))
        #TODO: this will overwrite two groups of the same id, need to change
        for group in source_groups.getListOfGroups():
            #for all the species that need to be converted, replace the ones that are
            #if the group is the species group, replace the ones detected from species_source_target
            if group.getId()==species_group_id or group.getId()==sink_species_group_id:
                for member in group.getListOfMembers():
                    if member.getIdRef() in species_source_target:
                        list_species = [i for i in species_source_target[member.getIdRef()]]
                        self.logger.debug('species_source_target: '+str(species_source_target))
                        self.logger.debug('list_species: '+str(list_species))
                        if len(list_species)==0:
                            self.logger.warning('Source species '+str(member.getIdRef())+' has been created in the target model')
                        elif len(list_species)>1:
                            self.logger.warning('There are multiple matches to the species '+str(member.getIdRef())+'... taking the first one: '+str(list_species))
                            #WARNING: taking the first one arbitrarely 
                            member.setIdRef(list_species[0])
                        else:
                            member.setIdRef(list_species[0])
            elif group.getId()==pathway_id:
                for member in group.getListOfMembers():
                    if member.getIdRef() in reac_replace:
                        member.setIdRef(reac_replace[member.getIdRef()])
            self._checklibSBML(target_groups.addGroup(group),
                    'copy the source groups to the target groups')
        ###### TITLES #####
        target_rpsbml.model.setId(target_rpsbml.model.getId()+'__'+source_rpsbml.model.getId())
        target_rpsbml.model.setName(target_rpsbml.model.getName()+' merged with '+source_rpsbml.model.getId())
        '''
        if fillOrphanSpecies==True:
            self.fillOrphan(target_rpsbml, self.pathway_id, compartment_id)
        '''
        return species_source_target, reac_replace


