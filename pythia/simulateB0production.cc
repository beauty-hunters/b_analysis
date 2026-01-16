#include <string>
#include <numeric>
#include <ctime>

#include <TFile.h>
#include <TNtuple.h>
#include <TH2F.h>

#include "Pythia8/Pythia.h"

void simulateB0production(int nEvents = 10000, int seed = 42, std::string tune = "monash", std::string outFileName = "b0_monash.root");
template <typename T>
int isPrimaryParticle(T &particle);

//__________________________________________________________________________________________________
void simulateB0production(int nEvents, int seed, std::string tune, std::string outFileName)
{

  //__________________________________________________________
  // create and configure pythia generator

  Pythia8::Pythia pythia;
  // switch off decays of interesting particles
  // pythia.readString("511:onMode = off");
  // pythia.readString("521:onMode = off");
  // pythia.readString("531:onMode = off");
  // defining tune
  pythia.readString("SoftQCD:inelastic = on");
  pythia.readString("Tune:pp = 14");
  if (tune == "monash")
  {
    pythia.readString("ColourReconnection:mode = 0");
    pythia.readString("StringPT:sigma = 0.335");
    pythia.readString("StringZ:aLund = 0.68");
    pythia.readString("StringZ:bLund = 0.98");
    pythia.readString("StringFlav:probQQtoQ = 0.081");
    pythia.readString("StringFlav:ProbStoUD = 0.217");
    pythia.readString("StringFlav:probQQ1toQQ0join = 0.5,0.7,0.9,1.0");
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.28");
    pythia.readString("BeamRemnants:remnantMode = 0");
  }
  else if (tune == "mode0")
  {
    pythia.readString("ColourReconnection:mode = 1");
    pythia.readString("ColourReconnection:allowDoubleJunRem = off");
    pythia.readString("ColourReconnection:m0 = 2.9");
    pythia.readString("ColourReconnection:allowJunctions = on");
    pythia.readString("ColourReconnection:junctionCorrection = 1.43");
    pythia.readString("ColourReconnection:timeDilationMode = 0");
    pythia.readString("StringPT:sigma = 0.335");
    pythia.readString("StringZ:aLund = 0.36");
    pythia.readString("StringZ:bLund = 0.56");
    pythia.readString("StringFlav:probQQtoQ = 0.078");
    pythia.readString("StringFlav:ProbStoUD = 0.2");
    pythia.readString("StringFlav:probQQ1toQQ0join = 0.0275,0.0275,0.0275,0.0275");
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.12");
    pythia.readString("BeamRemnants:remnantMode = 1");
    pythia.readString("BeamRemnants:saturation = 5");
  }
  else if (tune == "mode2")
  {
    pythia.readString("ColourReconnection:mode = 1");
    pythia.readString("ColourReconnection:allowDoubleJunRem = off");
    pythia.readString("ColourReconnection:m0 = 0.3");
    pythia.readString("ColourReconnection:allowJunctions = on");
    pythia.readString("ColourReconnection:junctionCorrection = 1.20");
    pythia.readString("ColourReconnection:timeDilationMode = 2");
    pythia.readString("ColourReconnection:timeDilationPar = 0.18");
    pythia.readString("StringPT:sigma = 0.335");
    pythia.readString("StringZ:aLund = 0.36");
    pythia.readString("StringZ:bLund = 0.56");
    pythia.readString("StringFlav:probQQtoQ = 0.078");
    pythia.readString("StringFlav:ProbStoUD = 0.2");
    pythia.readString("StringFlav:probQQ1toQQ0join = 0.0275,0.0275,0.0275,0.0275");
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.15");
    pythia.readString("BeamRemnants:remnantMode = 1");
    pythia.readString("BeamRemnants:saturation = 5");
  }
  else if (tune == "mode3")
  {
    pythia.readString("ColourReconnection:mode = 1");
    pythia.readString("ColourReconnection:allowDoubleJunRem = off");
    pythia.readString("ColourReconnection:m0 = 0.3");
    pythia.readString("ColourReconnection:allowJunctions = on");
    pythia.readString("ColourReconnection:junctionCorrection = 1.15");
    pythia.readString("ColourReconnection:timeDilationMode = 3");
    pythia.readString("ColourReconnection:timeDilationPar = 0.073");
    pythia.readString("StringPT:sigma = 0.335");
    pythia.readString("StringZ:aLund = 0.36");
    pythia.readString("StringZ:bLund = 0.56");
    pythia.readString("StringFlav:probQQtoQ = 0.078");
    pythia.readString("StringFlav:ProbStoUD = 0.2");
    pythia.readString("StringFlav:probQQ1toQQ0join = 0.0275,0.0275,0.0275,0.0275");
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.05");
    pythia.readString("BeamRemnants:remnantMode = 1");
    pythia.readString("BeamRemnants:saturation = 5");
  }
  else if (tune == "ropes")
  {
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.15");
    pythia.readString("BeamRemnants:remnantMode = 1");
    pythia.readString("BeamRemnants:saturation = 5");
    pythia.readString("ColourReconnection:mode = 1");
    pythia.readString("ColourReconnection:allowDoubleJunRem = off");
    pythia.readString("ColourReconnection:m0 = 0.3");
    pythia.readString("ColourReconnection:allowJunctions = on");
    pythia.readString("ColourReconnection:junctionCorrection = 1.2");
    pythia.readString("ColourReconnection:timeDilationMode = 2");
    pythia.readString("ColourReconnection:timeDilationPar = 0.18");
    pythia.readString("Ropewalk:RopeHadronization = on");
    pythia.readString("Ropewalk:doShoving = on");
    pythia.readString("Ropewalk:tInit = 1.5");
    pythia.readString("Ropewalk:deltat = 0.05");
    pythia.readString("Ropewalk:tShove 0.1");
    pythia.readString("Ropewalk:gAmplitude = 0.");
    pythia.readString("Ropewalk:doFlavour = on");
    pythia.readString("Ropewalk:r0 = 0.5");
    pythia.readString("Ropewalk:m0 = 0.2");
    pythia.readString("Ropewalk:beta = 0.1");
  }
  else if (tune == "srrc")
  {
    pythia.readString("ColourReconnection:mode = 1");
    pythia.readString("ColourReconnection:timeDilationMode = 0");
    pythia.readString("ColourReconnection:allowDoubleJunRem = off");
    pythia.readString("ColourReconnection:m0 = 1.05");
    pythia.readString("ColourReconnection:allowJunctions = on");
    pythia.readString("ColourReconnection:lambdaForm = 1");
    pythia.readString("ColourReconnection:mPseudo = 1.05");
    pythia.readString("ColourReconnection:junctionCorrection = 1.37");
    pythia.readString("ColourReconnection:dipoleMaxDist = 0.5");
    pythia.readString("StringPT:sigma = 0.335");
    pythia.readString("StringZ:aLund = 0.36");
    pythia.readString("StringZ:bLund = 0.56");
    pythia.readString("StringFlav:probQQtoQ = 0.078");
    pythia.readString("StringFlav:ProbStoUD = 0.4");
    pythia.readString("StringFlav:probQQ1toQQ0join = 0.5,0.7,0.9,1.0");
    pythia.readString("MultiPartonInteractions:pT0Ref = 2.37");
    pythia.readString("BeamRemnants:remnantMode = 1");
    pythia.readString("BeamRemnants:saturation = 5");
    pythia.readString("BeamRemnants:beamJunction = on");
    pythia.readString("ColourReconnection:heavyLambdaForm = 1");
    pythia.readString("StringFragmentation:pearlFragmentation = on");
  }

  pythia.readString("ParticleDecays:limitTau0 = on");
  pythia.readString("ParticleDecays:tau0Max = 10");
  pythia.readString("MiniStringFragmentation:tryAfterFailedFrag = on");

  // init
  pythia.readString("Random:setSeed = on");
  pythia.readString(Form("Random:seed = %d", seed));
  pythia.readString("Beams:eCM = 13600");
  pythia.init();

  TFile outFile(outFileName.data(), "recreate");
  TNtuple *ntupleB = new TNtuple("treeB", "treeB", "ptB:yB:pdgB");
  TH1D *hEvents = new TH1D("hEvents", "hEvents", 1, 0.5, 1.5);
  TH1D *hAcceptedEvents = new TH1D("hAcceptedEvents", "hAcceptedEvents", 1, 0.5, 1.5);
  TH1D *hSigmaGen = new TH1D("hSigmaGen", "hSigmaGen", 1, 0.5, 1.5);

  std::clock_t begin = clock();

  long unsigned nNonFailedEvents = 0;

  //__________________________________________________________
  // perform the simulation
  for (auto iEvent{0}; iEvent < nEvents; ++iEvent)
  {
    try
    {
      pythia.next();

      // fill tree of B mesons
      for (auto iPart{2}; iPart < pythia.event.size(); ++iPart)
      {
        int pdg = pythia.event[iPart].id();
        int absPdg = std::abs(pdg);
        if (absPdg != 511 && absPdg != 521 && absPdg != 531)
        {
          continue;
        }
        float y = pythia.event[iPart].y();
        if (std::abs(y) > 1.)
        {
          continue;
        }
        float pt = pythia.event[iPart].pT();

        ntupleB->Fill(pt, y, pdg);
      }
      ++nNonFailedEvents;
    }
    catch (const std::exception &e)
    {
      std::cerr << "Error in Pythia simulation: " << e.what() << std::endl;
    }
    if (iEvent % 100000 == 0)
    {
      std::clock_t end = clock();
      double elapsedSecs = double(end - begin) / CLOCKS_PER_SEC;
      std::cout << "Processed " << iEvent + 1 << " events in " << elapsedSecs << " s" << std::endl;
    }
  }

  hEvents->SetBinContent(1, nNonFailedEvents);
  hAcceptedEvents->SetBinContent(1, pythia.info.nAccepted());
  hSigmaGen->SetBinContent(1, pythia.info.sigmaGen());

  // save root output file
  ntupleB->Write();
  hEvents->Write();
  hAcceptedEvents->Write();
  hSigmaGen->Write();
  outFile.Close();
}

//__________________________________________________________________________________________________
template <typename T>
bool isPrimaryParticle(T &part)
{
  if (!part.isFinal() || !part.isCharged())
  {
    return false;
  }

  auto pdg = std::abs(part.id());
  if (pdg != 11 && pdg != 13 && pdg != 211 && pdg != 321 && pdg != 2212)
  { // it's not an e, mu, pi, K or p
    return false;
  }

  return true;
}