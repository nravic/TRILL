import esm
from esm.inverse_folding.util import load_structure, extract_coords_from_structure, score_sequence
from esm.inverse_folding.multichain_util import extract_coords_from_complex, sample_sequence_in_complex, score_sequence_in_complex
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
from transformers.models.esm.openfold_utils.protein import to_pdb, Protein as OFProtein
from transformers.models.esm.openfold_utils.feats import atom14_to_atom37

class coordDataset(torch.utils.data.Dataset):
    def __init__(self, input):
        self.input = input
    def __getitem__(self, idx):
        coords, seq = self.input[idx]
        return coords, seq
    def __len__(self):
        return len(self.input)

def ESM_IF1_Wrangle(infile):
    structures = load_structure(infile)
    data = extract_coords_from_complex(structures)
    data = coordDataset([data])
    return data

def ESM_IF1(data, genIters, temp):
    complex_flag = False
    model, alphabet = esm.pretrained.esm_if1_gvp4_t16_142M_UR50()
    model = model.eval()
    sampled_seqs = [()]
    native_seq_scores = [()]
    for batch in data:
        coords, native_seq = batch
        chains = list(coords.keys())
        if len(chains) > 1:
            complex_flag = True
        loop_chain = tqdm(chains)
        loop_chain.set_description('Chains')
        for coord in coords:
            coords[coord] = coords[coord].squeeze(0)
        for chain in loop_chain:
            loop_gen_iters = tqdm(range(int(genIters)))
            loop_gen_iters.set_description('Generative Iterations')
            if complex_flag == False:
                n_ll, _ = score_sequence(
                    model, alphabet, coords[chain], native_seq[chain])
            else:
                coords_4scoring = {}
                for k, v in coords.items():
                    coords_4scoring[k] = v.numpy()
                n_ll, _ = esm.inverse_folding.multichain_util.score_sequence_in_complex(
                        model, alphabet, coords_4scoring, chain, native_seq[chain][0]) 
                
            native_seq_scores.append(tuple([native_seq[chain], f'{chain}_{n_ll}']))
            for i in loop_gen_iters:
                sampled_seq = sample_sequence_in_complex(model, coords, chain, temperature=temp)
                if complex_flag == False:
                    ll, _ = score_sequence(
                    model, alphabet, coords[chain], sampled_seq)

                else:
                    try:
                        coords_4scoring = {}
                        for k, v in coords.items():
                            coords_4scoring[k] = v.numpy()
                        ll, _ = esm.inverse_folding.multichain_util.score_sequence_in_complex(
                        model, alphabet, coords_4scoring, chain, sampled_seq)

                    except ValueError:
                        print(f'{sampled_seq} could not be scored.')
                        ll = 'NA'
                sampled_seqs.append(tuple([sampled_seq, f'{chain}_{ll}']))
    sample_df = pd.DataFrame(sampled_seqs)
    sample_df = sample_df.iloc[1: , :]
    native_seq_scores = pd.DataFrame(native_seq_scores).iloc[1: , :]
    return sample_df, native_seq_scores

def clean_embeddings(model_reps):
    newdf = pd.DataFrame(model_reps, columns = ['Embeddings', 'Label'])
    finaldf = newdf['Embeddings'].apply(pd.Series)
    finaldf['Label'] = newdf['Label']
    return finaldf

def convert_outputs_to_pdb(outputs):
    final_atom_positions = atom14_to_atom37(outputs["positions"][-1], outputs)
    outputs = {k: v.to("cpu").numpy() for k, v in outputs.items()}
    final_atom_positions = final_atom_positions.cpu().numpy()
    final_atom_mask = outputs["atom37_atom_exists"]
    pdbs = []
    for i in range(outputs["aatype"].shape[0]):
        aa = outputs["aatype"][i]
        pred_pos = final_atom_positions[i]
        mask = final_atom_mask[i]
        resid = outputs["residue_index"][i] + 1
        pred = OFProtein(
            aatype=aa,
            atom_positions=pred_pos,
            atom_mask=mask,
            residue_index=resid,
            b_factors=outputs["plddt"][i],
            chain_index=outputs["chain_index"][i] if "chain_index" in outputs else None,
        )
        pdbs.append(to_pdb(pred))
    return pdbs
